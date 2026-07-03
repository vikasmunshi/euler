#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Interactive shell for v2: readline → lexer → parser → interpreter.

`SolverShell` reads command blocks (prompt-toolkit when interactive, plain
`input()` otherwise), lexes and parses them, and runs them through the v2
interpreter. Commands are dispatched through the shell's own registry (populated
by importing the command modules); the shell is the interpreter's command runner.
"""
from __future__ import annotations

__all__ = ['SolverShell']

import os
import re
import shlex
import sys
from contextlib import contextmanager
from typing import Any, Iterable, Iterator

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import clear_title, set_title
from rich.panel import Panel
from rich.text import Text

from solver.config import ExitCodes, config
from solver.shell.command import Context, registry
from solver.shell.interpreter import execute
from solver.shell.lexer import LexError, lex
from solver.shell.parser import ParserError, parse, set_commands
from solver.shell.session import SessionLog
from solver.shell.tty import console, make_session, read_blocks, trim_history
from solver.shell.variables import variables

#: A variable reference being typed at the cursor: `{` then an optional partial
#: name. Used to switch completion from command names to variable names.
_REF_PREFIX_RE = re.compile(r'\{([a-z][a-z0-9_]*)?$')


def _var_meta(name: str) -> str:
    """A short right-hand hint for a variable completion (its value, or 'computed').

    Callable specials (the dynamic ones — `next`, `random`, …) are *not* invoked;
    their hint is just 'computed'. Other values are shown via a truncated `repr`.
    """
    try:
        value = variables[name]
    except KeyError:
        return ''
    if callable(value):
        return 'computed'
    text = repr(value)
    return text if len(text) <= 40 else f'{text[:37]}...'


def _current_fragment(text: str) -> str:
    """Return the command being typed after the last unquoted statement separator."""
    quote: str | None = None
    start = i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if quote is not None:
            if c == quote:
                quote = None
        elif c in ('"', "'"):
            quote = c
        elif c in (';', '{', '}', '\n'):
            start = i + 1
        elif c in ('&', '|') and i + 1 < n and text[i + 1] == c:
            start = i + 2
            i += 2
            continue
        i += 1
    return text[start:]


class _CommandCompleter(Completer):
    """Complete command names on the first token; delegate to per-command completers."""

    def __init__(self, shell: 'SolverShell') -> None:
        self._shell = shell

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Yield completions for the text before the cursor.

        Completes a `{partial` variable reference to `{name}`, the first token to a
        command name, and any later token by delegating to the resolved command's
        own completer (mirroring the parser's `!`/`?` sigil split).
        """
        before = document.text_before_cursor
        # Variable reference: a `{partial` at the cursor completes to `{name}`.
        ref = _REF_PREFIX_RE.search(before)
        if ref is not None and not before[:ref.start()].endswith('{'):  # not an escaped `{{`
            partial = ref.group(1) or ''
            for name in sorted(variables.vars()):
                if name.startswith(partial):
                    yield Completion(f'{{{name}}}', start_position=-(len(partial) + 1),
                                     display=f'{{{name}}}', display_meta=_var_meta(name))
            return
        text = _current_fragment(before)
        # Mirror the parser's sigil split ('!ls' -> '! ls', '?ec' -> '? ec') so a
        # sigil abutting its argument delegates to the right command's completer.
        if text[:1] in ('!', '?') and text[1:2] not in ('', ' '):
            text = f'{text[0]} {text[1:]}'
        try:
            tokens = shlex.split(text, posix=True)
        except ValueError:
            tokens = text.split()
        if not tokens or (text and not text.endswith(' ') and len(tokens) == 1):
            prefix = tokens[0] if tokens else ''
            for name in self._shell.registry.names():
                if name.startswith(prefix):
                    yield Completion(name, start_position=-len(prefix))
            return
        cmd = self._shell.registry.resolve(tokens[0])
        if cmd is None or cmd.completer is None:
            return
        partial = '' if text.endswith(' ') else tokens[-1]
        ctx = Context(shell=self._shell, console=self._shell.console, raw_line=text, argv=tokens[1:])
        for candidate in cmd.completer(ctx, partial):
            if isinstance(candidate, Completion):
                yield candidate
            elif candidate.startswith(partial):
                yield Completion(candidate, start_position=-len(partial))


class SolverShell:
    """Interactive shell built on prompt-toolkit + rich, running the v2 pipeline."""

    def __init__(self, *, save: bool = False) -> None:
        self.console = console
        self.registry = registry
        self.save = save
        self._session_log: SessionLog | None = None
        set_commands(self.registry.names())

    # -- command-host surface (consumed by commands via ctx.shell) ----------

    @property
    def rc(self) -> int:
        """The standing exit code (the most recent evaluation's status)."""
        return int(variables['rcode'])

    @property
    def is_logging(self) -> bool:
        """True while a session log is open and command output is being tee'd.

        Lets commands that spawn subprocesses decide whether to route output
        through `sys.stdout` (so it reaches the log) or let the child inherit the
        terminal directly (preserving its TTY colours when not logging).
        """
        return self._session_log is not None

    @contextmanager
    def _capture(self) -> Iterator[None]:
        """Tee command output into the session log, if one is active."""
        if self._session_log is None:
            yield
        else:
            with self._session_log.capture():
                yield

    @contextmanager
    def pause_logging(self) -> Iterator[None]:
        """Suspend session-log capture for the duration (terminal output continues).

        Keeps a high-frequency live region's redraws out of the transcript while
        still showing them live; a no-op when no log is active.
        """
        if self._session_log is None:
            yield
        else:
            with self._session_log.pause():
                yield

    def _record_command(self, block: str) -> None:
        """Record an entered block in the session log, if active."""
        if self._session_log is not None and block.strip():
            self._session_log.record_command('TBD', block)

    @contextmanager
    def _runtime(self) -> Iterator[None]:
        """Per-run setup/teardown: enter the repo root and, when `save` is set,
        open the session log for the duration, closing it on exit."""
        os.chdir(config.root_dir)
        if self.save:
            self._session_log = SessionLog(config.session_file)
        try:
            yield
        finally:
            if self._session_log is not None:
                self._session_log.close()
                self._session_log = None

    # -- command runner (the interpreter's dispatch hook) -------------------

    def _run_command(self, name: str, args: list[str]) -> int:
        """Resolve and invoke command *name* with *args*; the interpreter's dispatch hook.

        Returns the command's exit code, or EXIT_NOTFOUND after reporting an
        unknown command.
        """
        cmd = self.registry.resolve(name)
        if cmd is None:
            self.console.print(f'[error]unknown command:[/error] {name}')
            return ExitCodes.EXIT_NOTFOUND
        raw = ' '.join([name, *(shlex.quote(a) for a in args)])
        ctx = Context(shell=self, console=self.console, variables=variables, raw_line=raw, argv=list(args))
        return cmd.invoke(ctx)

    # -- dispatch -----------------------------------------------------------

    def dispatch(self, block: str) -> int:
        """Lex, parse, and interpret one command block; return its exit code."""
        self._record_command(block)
        with self._capture():
            try:
                canonical = lex(block)
            except LexError as exc:
                self._show_syntax_error(exc, canonical=None)
                return ExitCodes.EXIT_USAGE
            try:
                loop, statements = parse(canonical)
            except ParserError as exc:
                self._show_syntax_error(exc, canonical=canonical)
                return ExitCodes.EXIT_USAGE
            return execute(loop, statements, command=self._run_command)

    def _show_syntax_error(self, exc: LexError | ParserError, canonical: str | None) -> None:
        """Report a lex/parse failure as a clean, positioned message.

        A `LexError`'s text is already `message`, then the offending line and a
        `^` caret with `(line, col)`; that first line becomes the headline and
        the rest is shown verbatim (the caret aligns under the printed line). A
        `ParserError` carries no caret, so the lexer's **canonical** form (the
        text being parsed) is shown as context instead.
        """
        head, _, located = str(exc).partition('\n')
        out = Text()
        out.append('syntax error: ', style='error')
        out.append(head, style='error')
        if located:
            out.append('\n')
            out.append(located, style='warning')
        elif canonical is not None:
            out.append('\n\n')
            out.append('while parsing:\n', style='muted')
            out.append('\n'.join(f'  {line}' for line in canonical.splitlines()), style='muted')
        self.console.print(out)

    # -- lifecycle ----------------------------------------------------------

    def run_command(self, blocks: list[str]) -> int:
        """Execute *blocks* non-interactively; return the last exit status."""
        with self._runtime():
            rc = 0
            for block in blocks:
                print(block)
                if not block.strip():
                    continue
                try:
                    rc = self.dispatch(block)
                except SystemExit as exit_signal:
                    return int(exit_signal.code) if isinstance(exit_signal.code, int) else 0
                except KeyboardInterrupt:
                    self.console.print('[muted]^C[/muted]')
                    break
            return rc

    def run_interactive(self, intro: bool = True, intro_message: str = '') -> int:
        """Run the interactive prompt loop until `exit` / EOF; return the status."""
        with self._runtime():
            # Piped/redirected stdin: read blocks without the interactive chrome
            # (no banner, no history, no prompt) so scripted output stays clean.
            if not sys.stdin.isatty():
                return self._run_piped()
            if intro:
                self.console.clear()
                self._print_banner()
            if intro_message:
                self.console.print(intro_message)
            trim_history(config.history_file)
            last_problem = self._load_last_problem()
            session = make_session(
                history_file=config.history_file,
                completer=_CommandCompleter(self),
                style=config.style,
                bottom_toolbar=self._bottom_toolbar,
            )
            try:
                while True:
                    try:
                        set_title(f'solver · {variables.problem}')
                        block = session.prompt(self._prompt())
                    except KeyboardInterrupt:
                        self.console.print('[muted]^C[/muted]')
                        continue
                    except EOFError:
                        break
                    if not block.strip():
                        continue
                    try:
                        self.dispatch(block)
                    except SystemExit:
                        break
                    except KeyboardInterrupt:
                        self.console.print('[muted]^C[/muted]')
                    finally:
                        last_problem = self._persist_last_problem(last_problem)
            finally:
                clear_title()
                self._persist_last_problem(last_problem)
                trim_history(config.history_file)
            if intro:
                self.console.print('[muted]session ended.[/muted]')
            return self.rc

    def _run_piped(self) -> int:
        """Dispatch blocks read from non-interactive stdin; return the final status."""
        for block in read_blocks(prompt='', continuation=''):
            try:
                self.dispatch(block)
            except SystemExit:
                break
        return self.rc

    # -- per-user last-problem persistence ----------------------------------

    def _load_last_problem(self) -> int | None:
        """Seed the active problem from the per-user last-problem file.

        Returns the number now in effect (so the caller can suppress a redundant
        first write), or None when there is nothing valid to restore — a missing
        file, unparseable content, or a problem number that is no longer known.
        """
        try:
            number = int(config.last_problem_file.read_text(encoding='utf-8').strip())
        except (OSError, ValueError):
            return None
        try:
            variables.set_problem(number)
        except ValueError:
            return None
        return number

    def _persist_last_problem(self, last: int | None) -> int | None:
        """Write the active problem number if it changed since *last*; return what is on disk.

        A best-effort atomic write (temp file + `os.replace`); any failure — or an
        unresolvable current problem — leaves the file untouched and never disturbs
        the shell.
        """
        try:
            number = variables.problem.number
        except Exception:  # noqa: BLE001 — persistence must never break the shell
            return last
        if number == last:
            return last
        tmp = config.last_problem_file.with_suffix('.tmp')
        try:
            tmp.write_text(f'{number}\n', encoding='utf-8')
            os.replace(tmp, config.last_problem_file)
        except OSError:
            return last
        return number

    # -- UI -----------------------------------------------------------------

    def _prompt(self) -> FormattedText:
        """Build the interactive prompt: a bar, the current problem, and the `❯` symbol."""
        return FormattedText([
            ('class:prompt.bar', '▎'),
            ('class:prompt.path', f' {variables.problem} ',),
            ('class:prompt.symbol', '❯ '),
        ])

    def _bottom_toolbar(self) -> FormattedText:
        """Build the bottom toolbar showing the command count and exit hint."""
        n = len(self.registry.all())
        return FormattedText([
            ('class:bottom-toolbar', f' solver v2 · {n} commands · Ctrl-D to exit '),
        ])

    def _print_banner(self) -> None:
        """Print the welcome banner shown when the interactive shell starts."""
        body = Text.from_markup(
            '[accent]SOLVER[/accent]  [muted]v2[/muted]\n'
            '[primary]  Your Euler problem solving companion in the terminal[/primary]\n'
            '[muted]  Powered by [accent.dim]claude.ai[/accent.dim]'
            ' · [accent.dim]prompt-toolkit[/accent.dim]'
            ' · [accent.dim]rich[/accent.dim]\n\n'
            '  start with [accent.dim]ls \\[number|next|random][/accent.dim],'
            ' then [accent.dim]eval[/accent.dim]/[accent.dim]benchmark[/accent.dim]\n'
            '[accent]  ?[/accent] help[/muted]'
        )
        self.console.print(Panel(
            body,
            border_style='panel.border',
            title='[accent]▎[/accent] [primary]solver[/primary]',
            subtitle='[muted]type [/muted][accent]exit[/accent][muted] or [/muted]'
                     '[accent]Ctrl-D[/accent][muted] to quit[/muted]',
            title_align='left',
            subtitle_align='right',
            padding=(1, 2),
        ))
