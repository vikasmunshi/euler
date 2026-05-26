#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Experimental interactive shell built on prompt-toolkit and rich.

Replaced the earlier 'Cmd' based framework.
Functionally equivalent, but with a more modern and flexible look and feel.

Design goals
------------
* Look and feel inspired by the Junie UI: a soft, modern terminal aesthetic
  with rounded panels, subtle colours, a left-side accent bar, and a compact
  status footer.
* Strict separation between the *framework* (this file) and *commands*
  (to be added in sibling modules).
* Async-friendly prompt loop powered by 'prompt_toolkit.PromptSession' with
  history, auto-suggest, completion, and key bindings.
* Rich-rendered output via a shared: class:`rich.console.Console`.
"""
from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO

from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from solver.config import config

#: Shared console instance; used by the shell and importable by command modules.
console: Console = Console(theme=config.theme, highlight=False)


# ---------------------------------------------------------------------------
# Command framework
# ---------------------------------------------------------------------------

@dataclass
class Context:
    """Runtime context passed to every command invocation.

    Commands receive this as their first argument.  It exposes the shared
    :class:`rich.console.Console` together with the owning shell so commands
    can introspect or mutate shell state (e.g. exit, reload, register new
    commands at runtime).
    """
    shell: 'SolverShell'
    console: Console
    raw_line: str = ''
    argv: list[str] = field(default_factory=list)


#: Signature of a command callable.  Extra positional / keyword arguments are
#: parsed from the user's input line via :func:`shlex.split`.
CommandFn = Callable[..., bool | None]


@dataclass
class Command:
    """A registered shell command.

    Attributes
    ----------
    name:
        Primary command name (the first whitespace-separated token on the
        input line).
    func:
        Callable invoked with a :class:`Context` followed by parsed argv
        tokens.  May return 'True' to request that the shell exit.
    help:
        Short one-line help string, shown in the 'help' listing.
    usage:
        Optional usage signature, shown by 'help <cmd>'.
    aliases:
        Alternative names that resolve to this command.
    completer:
        Optional callable '(ctx, text) -> list[str]' producing argument
        completions for the command.
    """
    name: str
    func: CommandFn
    help: str = ''
    usage: str = ''
    aliases: tuple[str, ...] = ()
    completer: Callable[[Context, str], Iterable[str | Completion]] | None = None

    def invoke(self, ctx: Context) -> bool | None:
        return self.func(ctx, *ctx.argv)


class CommandRegistry:
    """Registry of :class:`Command` instances, keyed by name and alias.

    A module-level :data:`registry` is provided for convenience; you may also
    instantiate private registries for embedded shells.
    """

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._by_alias: dict[str, str] = {}

    def register(self, cmd: Command) -> Command:
        """Register *cmd*; raises :class:`ValueError` on name/alias conflict."""
        if cmd.name in self._commands or cmd.name in self._by_alias:
            raise ValueError(f'command {cmd.name!r} is already registered')
        self._commands[cmd.name] = cmd
        for alias in cmd.aliases:
            if alias in self._commands or alias in self._by_alias:
                raise ValueError(f'alias {alias!r} conflicts with existing command')
            self._by_alias[alias] = cmd.name
        return cmd

    def unregister(self, name: str) -> None:
        cmd = self._commands.pop(name, None)
        if cmd is None:
            return
        for alias in cmd.aliases:
            self._by_alias.pop(alias, None)

    def resolve(self, token: str) -> Command | None:
        if token in self._commands:
            return self._commands[token]
        target = self._by_alias.get(token)
        return self._commands.get(target) if target else None

    def names(self, include_aliases: bool = True) -> list[str]:
        out = list(self._commands)
        if include_aliases:
            out.extend(self._by_alias)
        return sorted(out)

    def all(self) -> list[Command]:
        return sorted(self._commands.values(), key=lambda c: c.name)


#: Default, module-level registry used by the :func:`command` decorator.
registry = CommandRegistry()


def command(
        name: str | None = None,
        *,
        help: str = '',
        usage: str = '',
        aliases: tuple[str, ...] = (),
        completer: Callable[[Context, str], Iterable[str | Completion]] | None = None,
) -> Callable[[CommandFn], CommandFn]:
    """Decorator that registers *func* as a shell command.

    Example
    -------
    >>> @command(name='echo', help='Echo arguments.', aliases=('e',))
    ... def _echo(ctx: Context, *args: str) -> None:
    ...     ctx.console.print(' '.join(args))
    """

    def _decorate(func: CommandFn) -> CommandFn:
        cmd_name = name or func.__name__.lstrip('_').replace('_', '-')
        cmd_help = help
        if not cmd_help and func.__doc__:
            cmd_help = func.__doc__.strip().splitlines()[0]
        registry.register(Command(
            name=cmd_name,
            func=func,
            help=cmd_help,
            usage=usage,
            aliases=tuple(aliases),
            completer=completer,
        ))
        return func

    return _decorate


# ---------------------------------------------------------------------------
# prompt-toolkit glue
# ---------------------------------------------------------------------------

class _ShellCompleter(Completer):
    """Completer that delegates to per-command completers after the first token."""

    def __init__(self, shell: 'SolverShell') -> None:
        self._shell = shell

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        text_before = document.text_before_cursor
        try:
            tokens = shlex.split(text_before, posix=True)
        except ValueError:
            tokens = text_before.split()
        # First word: complete command names.
        if not tokens or (text_before and not text_before.endswith(' ') and len(tokens) == 1):
            prefix = tokens[0] if tokens else ''
            for name in self._shell.registry.names():
                if name.startswith(prefix):
                    yield Completion(name, start_position=-len(prefix))
            return
        # Subsequent words: delegate to command completer if available.
        head = tokens[0]
        cmd = self._shell.registry.resolve(head)
        if cmd is None or cmd.completer is None:
            return
        partial = '' if text_before.endswith(' ') else tokens[-1]
        ctx = Context(shell=self._shell, console=self._shell.console,
                      raw_line=text_before, argv=tokens[1:])
        for candidate in cmd.completer(ctx, partial):
            if isinstance(candidate, Completion):
                yield candidate
            elif candidate.startswith(partial):
                yield Completion(candidate, start_position=-len(partial))


# ---------------------------------------------------------------------------
# Multi-line block detection
# ---------------------------------------------------------------------------

@Condition
def _block_is_open() -> bool:
    """True while the current buffer contains more '{' than '}'.

    Used as the *multiline* condition for :class:`PromptSession`: when this
    returns True, Enter inserts a newline instead of submitting the input,
    allowing brace-delimited blocks (e.g. 'for' loops) to span lines.
    """
    try:
        text = get_app().current_buffer.text
        return text.count('{') > text.count('}')
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------

@dataclass
class SolverShell:
    """Interactive shell built on prompt-toolkit + rich.

    Parameters
    ----------
    registry:
        Command registry to use.  Defaults to the module-level
        :data:`registry`, so commands declared with :func:`command` are
        picked up automatically.
    history_file:
        Path to a persistent history file (created on first use).
    workspace:
        Free-form label shown in the prompt; typically the current
        workspace path.
    """

    registry: CommandRegistry = field(default_factory=lambda: registry)
    history_file: Path = field(default_factory=lambda: config.history_file)
    workspace: Path = field(default_factory=lambda: config.workspace_dir)
    console: Console = field(default_factory=lambda: console)
    save: bool = False

    _running: bool = field(default=False, init=False, repr=False)
    _session: PromptSession = field(default=None, init=False, repr=False)  # type: ignore [arg-type]
    _save_file: TextIO | None = field(default=None, init=False, repr=False)

    # -- save / tee helpers ------------------------------------------------

    def _flush_save(self) -> None:
        """Drain the console's record buffer into the save file."""
        if self._save_file is None:
            return
        text = self.console.export_text(clear=True, styles=False)
        if text:
            self._save_file.write(text)
            self._save_file.flush()

    def _record_input(self, line: str) -> None:
        """Append the user's typed prompt line directly to the save file.

        prompt-toolkit draws the prompt outside Rich's recording stream, so
        the typed input would otherwise be missing from the saved log.
        """
        if self._save_file is None:
            return
        self._save_file.write(f'▎ {self.workspace.name} ❯ {line}\n')
        self._save_file.flush()

    # -- history maintenance -----------------------------------------------

    def _trim_history(self, max_entries: int = 5000) -> None:
        """Deduplicate the FileHistory file and cap it at *max_entries* entries.

        Keeps the most recent occurrence of each unique command and at most
        the newest *max_entries* unique entries.  Safe to call when the file
        is missing or unreadable.
        """
        path = self.history_file
        if not path.exists():
            return
        try:
            raw = path.read_text(encoding='utf-8')
        except OSError:
            return
        entries: list[tuple[str, str]] = []
        current_ts: str | None = None
        current_lines: list[str] = []
        for line in raw.splitlines():
            if line.startswith('# '):
                if current_ts is not None and current_lines:
                    entries.append((current_ts, '\n'.join(current_lines)))
                current_ts = line
                current_lines = []
            elif line.startswith('+'):
                current_lines.append(line[1:])
        if current_ts is not None and current_lines:
            entries.append((current_ts, '\n'.join(current_lines)))
        seen: set[str] = set()
        kept: list[tuple[str, str]] = []
        for ts, text in reversed(entries):
            if text in seen:
                continue
            seen.add(text)
            kept.append((ts, text))
            if len(kept) >= max_entries:
                break
        kept.reverse()
        tmp = path.with_suffix(path.suffix + '.tmp')
        try:
            with tmp.open('w', encoding='utf-8') as f:
                for ts, text in kept:
                    f.write(f'\n{ts}\n')
                    for line in text.split('\n'):
                        f.write(f'+{line}\n')
            os.replace(tmp, path)
        except OSError:
            try:
                tmp.unlink()
            except OSError:
                pass

    # -- lifecycle ----------------------------------------------------------

    def run(self, intro: bool = True, commands: list[str] | None = None) -> int:
        """Run the prompt loop until the user exits.  Returns a process exit code.

        Parameters
        ----------
        intro:
            If True, print the welcome banner before entering the loop.
        commands:
            Optional list of commands to execute at startup (e.g. from the
            CLI).  Each entry is dispatched as if typed at the prompt; if any
            command requests exit (e.g. 'exit'), the loop terminates before
            entering interactive mode.
        """
        os.chdir(self.workspace)
        self._trim_history()
        if self.save:
            self.console.record = True
            self._save_file = open(config.session_file, 'w', encoding='utf-8')
        self._session: PromptSession = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=_ShellCompleter(self),
            complete_while_typing=True,
            key_bindings=self._build_keybindings(),
            style=config.style,
            bottom_toolbar=self._bottom_toolbar,
            multiline=_block_is_open,
            prompt_continuation=FormattedText([('class:prompt.bar', '▎'), ('class:prompt.symbol', ' · '), ]),
        )
        try:
            if intro:
                self._print_banner()
            self._running = True
            # Replay any startup commands first; abort the interactive loop if one exits.
            for line in commands or []:
                if not line.strip():
                    continue
                try:
                    self.console.print(
                        f'[accent]▎[/accent] [primary]{self.workspace.name}[/primary] '
                        f'[accent]❯[/accent] {line}')
                    try:
                        if self.dispatch(line):
                            self._running = False
                            break
                    except KeyboardInterrupt:
                        self.console.print('[muted]^C[/muted]')
                        continue
                    except SystemExit:
                        raise
                    except EOFError:
                        break
                    except Exception as exc:  # noqa: BLE001
                        self.console.print(f'[error]error:[/error] {exc}')
                finally:
                    self._flush_save()
            while self._running:
                try:
                    try:
                        line = self._session.prompt(self._build_prompt())
                    except KeyboardInterrupt:
                        self.console.print('[muted]^C[/muted]')
                        continue
                    except EOFError:
                        break
                    if not line.strip():
                        continue
                    self._record_input(line)
                    try:
                        if self.dispatch(line):
                            break
                    except KeyboardInterrupt:
                        self.console.print('[muted]^C[/muted]')
                        continue
                    except SystemExit:
                        raise
                    except Exception as exc:  # noqa: BLE001 — top-level UX boundary
                        self.console.print(f'[error]error:[/error] {exc}')
                finally:
                    self._flush_save()
            self._print_farewell()
        finally:
            if self._save_file is not None:
                self._flush_save()
                self._save_file.close()
                self._save_file = None
            self._trim_history()
        return 0

    # -- dispatch -----------------------------------------------------------

    def dispatch(self, line: str) -> bool:
        """Parse *line* and dispatch to a registered command.

        Returns 'True' if the shell should exit.
        Lines beginning with a sigil ('!', '?') are rewritten so the
        sigil itself becomes the command name (with the remainder as its
        argument), e.g. '!ls' -> '! ls'.
        """
        stripped = line.lstrip()
        if stripped and stripped[0] in ('!', '?') and (len(stripped) == 1 or stripped[1] != ' '):
            line = f'{stripped[0]} {stripped[1:]}'
        try:
            tokens = shlex.split(line, posix=True)
        except ValueError as exc:
            self.console.print(f'[error]parse error:[/error] {exc}')
            return False
        if not tokens:
            return False
        head, *argv = tokens
        cmd = self.registry.resolve(head)
        if cmd is None:
            self.console.print(f'[error]unknown command:[/error] {head}  '
                               f'[muted](try [accent]help[/accent])[/muted]')
            return False
        ctx = Context(shell=self, console=self.console, raw_line=line, argv=argv)
        try:
            return bool(cmd.invoke(ctx))
        finally:
            self._flush_save()

    def stop(self) -> None:
        """Request the prompt loop to exit after the current iteration."""
        self._running = False

    # -- UI helpers ---------------------------------------------------------

    def _build_prompt(self) -> FormattedText:
        # a vertical accent bar, the workspace path, then a chevron.
        return FormattedText([
            ('class:prompt.bar', '▎'),
            ('class:prompt.path', f' {self.workspace.name} '),
            ('class:prompt.symbol', '❯ '),
        ])

    def _bottom_toolbar(self) -> FormattedText:
        n = len(self.registry.all())
        return FormattedText([
            ('class:bottom-toolbar', f' solver · {n} commands · Ctrl-D to exit '),
        ])

    def _build_keybindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add('c-l')
        def _(event: KeyPressEvent) -> None:
            event.app.renderer.clear()

        return kb

    _LOGO: str = (
        'SOLVER\n'
    )

    def _print_banner(self) -> None:
        # a big accent-colored wordmark, a soft tagline,
        # and a compact "tips" footer — all wrapped in a rounded panel with
        # a left-side accent bar in the title.
        logo = Text(self._LOGO, style='accent', no_wrap=True)
        tagline = Text.from_markup(
            '[primary]  Your Euler problem solving companion in the terminal[/primary]'
            '\n'
            '[muted]  Powered by [/muted]'
            '[accent.dim]claude.ai[/accent.dim]'
            '[muted] · [/muted]'
            '[accent.dim]prompt-toolkit[/accent.dim]'
            '[muted] · [/muted]'
            '[accent.dim]rich[/accent.dim]'
            '\n\n'
            '[muted]  start with [/muted]'
            '[accent.dim]init <number|next|random>[/accent.dim]'
            '[muted] to initialize the workspace with problem files[/muted]'
            '\n'
            '[accent.dim]  show[/accent.dim]'
            '[muted] to read the problem documentation[/muted]'
            '\n'
            '[accent.dim]  eval[/accent.dim]'
            '[muted] and [/muted]'
            '[accent.dim]benchmark[/accent.dim]'
            '[muted] to check your solutions[/muted]'
            '\n'
            '[accent.dim]  stack[/accent.dim]'
            '[muted]/[/muted]'
            '[accent.dim]reset[/accent.dim]'
            '[muted] to save/discard[/muted]'
            '\n\n'
            '[accent]  ?[/accent]'
            '[muted] help   [/muted]'
            '[accent]![/accent]'
            '[muted] bash[/muted]'
        )
        body = Text('\n').join([logo, tagline])
        self.console.print(Panel(
            body,
            border_style='panel.border',
            title='[accent]▎[/accent] [primary]solver[/primary]',
            subtitle='[muted]type [/muted][accent]exit[/accent][muted] '
                     'or press [/muted][accent]Ctrl-D[/accent][muted] to quit[/muted]',
            title_align='left',
            subtitle_align='right',
            padding=(1, 2),
        ))

    def _print_farewell(self) -> None:
        self.console.print('[muted]session ended.[/muted]')


__all__ = (
    'Context',
    'SolverShell',
    'command',
    'console',
)
