#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Every question the shell asks: one interaction model, in one place.

Before this module each command asked in its own dialect — three affirmative conventions
(`yes` / `m/s/q` / `y/n`), two quit words, two exit codes for the same "user said no", and a
prompt that dumped an `EOFError` traceback whenever stdin was a pipe. The primitives here are
the whole vocabulary; nothing outside this module calls `console.input`.

Three rules hold for all of them.

**Line-based, never full-screen.** Every prompt reads one line through the shared console, so
a dialogue behaves identically in a terminal, in the browser's PTY (`solver/web/ws`), and in a
`solver -s` session log, which tees typed input. A curses picker would work in none of those.
The polish comes from what is rendered *around* the prompt line — numbered tables, panels,
counters — not from taking over the screen.

**Never crash, never hang.** :func:`interactive` is the one guard: a tty on stdin, a terminal
on stdout, and not muted by `--silent`. EOF and `Ctrl-C` raise :class:`Abort`, never a
traceback. A dialogue that cannot be shown raises :class:`Abort` too, carrying the exit code
and a message naming what to pass instead.

**Declining is not success.** :class:`Abort` carries `ExitCodes.EXIT_ABORT`, so a chain gated
on the command stops: `gh-merge merge && git-push` no longer pushes after you quit the review.

Two models are built on this (`docs/developer-guide.md` §3.10). *In-command dialogues* —
:func:`confirm`, :func:`sure`, :func:`pause`, :func:`walk` — are for questions whose answer is
not an argument. Questions whose answer *is* an argument belong to the register contract's
`Ask` (§3.11), declared on the parameter and served by :func:`choose` / :func:`text`, so the
command body never grows an `if not thread:` block.
"""
from __future__ import annotations

__all__ = ['Abort', 'Action', 'Ask', 'Choice', 'Choices', 'Choosable', 'MENU_MAX', 'SKIP',
           'WalkResult', 'as_choice', 'choose', 'confirm', 'interactive', 'pause', 'secret',
           'select', 'sure', 'text', 'walk']

import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence, runtime_checkable

from rich.table import Table
from rich.text import Text

from solver.config import ExitCodes
from solver.shell.tty import console

#: Above this many options a menu stops being readable, so :func:`choose` switches to the
#: search-and-filter flow instead of printing the lot. About a screenful.
MENU_MAX: int = 12


class Abort(Exception):
    """The user declined, quit, or could not be asked.

    Raised by every primitive here and mapped to an exit code by the `@register` adapter, so a
    command body reads as a straight line: ask, act. `rc` defaults to
    `ExitCodes.EXIT_ABORT` — non-zero, so `&&` stops — and becomes `EXIT_USAGE` when the
    question could not be put at all and the fix is to pass an argument.
    """

    def __init__(self, message: str = 'aborted', rc: int = ExitCodes.EXIT_ABORT) -> None:
        super().__init__(message)
        self.message = message
        self.rc = rc


@dataclass(frozen=True)
class Choice:
    """One option in a menu: the value bound to the argument, plus what the user reads."""
    value: str
    label: str = ''
    description: str = ''

    @property
    def text(self) -> str:
        """The label to show, falling back to the value."""
        return self.label or self.value


@runtime_checkable
class Choosable(Protocol):
    """An object that knows how to offer itself in a menu.

    Lets one list serve two surfaces: a `loop` body wants the object (`{loop.number}`,
    `{loop.branch}`), a menu wants a row to read. Without it a choice set would have to be
    built as `Choice`s and lose everything the body could have used, or built twice.
    """

    def __choice__(self) -> Choice: ...


def as_choice(value: Any) -> Choice:
    """Render *value* as a menu option: a `Choice`, a `Choosable`, or its string form."""
    if isinstance(value, Choice):
        return value
    if isinstance(value, Choosable):
        return value.__choice__()
    return Choice(str(value))


#: Builds a menu's options when the dialogue fires. Receives the live `Context` and the
#: arguments bound so far, so a choice set can narrow by an earlier answer — `msg act` labels
#: each message with what acting on it would do. Called once, never at import, never when the user typed
#: the answer.
Choices = Callable[[Any, dict[str, Any]], Sequence[Choice]]

#: Decides whether a parameter is worth asking about at all, given the arguments bound so far.
Predicate = Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class Ask:
    """Declares that the adapter may ask for a parameter the user left out.

    Attached to the parameter through `Annotated[T, Ask(...)]` rather than to the command
    through a decorator flag, for three reasons. A command function stays an ordinary Python
    callable, so it keeps a real default and mypy stays happy. A default is *not* the same as
    "no answer yet" — nearly every candidate parameter already has one, so "ask for missing
    required arguments" would never fire where it is wanted. And a requirement is often
    conditional (`msg` needs a subject only for `send`), which `when` states next to the
    parameter instead of in a validation ladder.

    Non-interactively nothing is asked and the parameter keeps its default: a scripted
    `solver "msg"` still lists, exactly as before.
    """
    question: str = ''
    #: Where the options come from. A **string names a shell variable** (`choices='open_prs'`),
    #: which is the usual case: the list is then one declaration serving both a menu here and
    #: `loop {open_prs}:` in a block. A callable is for the rest — a set that has to narrow by
    #: an earlier answer, which a variable cannot see. None derives the options from the
    #: annotation — `Literal` members, enum values, `bool` — so a static set needs neither.
    choices: Choices | str | None = None
    when: Predicate | None = None
    #: Shown when `choices` comes back empty: the emptiness is the answer ("no messages to
    #: read"), which a prefix-filtering completer could never tell us.
    empty: str = ''
    #: Read the answer as hidden input (a password), or over several lines until a blank one.
    secret: bool = False
    multiline: bool = False
    #: Enter accepts nothing and moves on, because nothing is a real answer here — an angle
    #: for the writer, say. Off by default: for most questions an empty line is not an
    #: answer, and re-asking is kinder than acting on it.
    skippable: bool = False
    #: Accept only a listed value, re-asking otherwise — so a bad id is caught here rather
    #: than by the service it would have been sent to.
    strict: bool = True
    #: Reading text for the members of a `Literal`, keyed by member. The annotation stays the
    #: source of what is *valid*; this only says what each option means, so a menu of verbs
    #: reads like the docstring rather than like a type.
    labels: Mapping[str, str] | None = None


@dataclass(frozen=True)
class Action:
    """One key in a :func:`walk`: what it is called, and what it does to an item."""
    name: str
    run: Callable[[Any], int | None]


#: A `walk` action that does nothing to the item — the explicit "leave it as it is".
SKIP: Callable[[Any], int | None] = lambda _: None  # noqa: E731 — a named sentinel reads better


@dataclass
class WalkResult:
    """What a :func:`walk` did: how many items took each action, and whether it was quit."""
    counts: dict[str, int] = field(default_factory=dict)
    quit: bool = False

    @property
    def rc(self) -> int:
        """`EXIT_ABORT` when the user quit part-way, `EXIT_OK` when the queue was worked."""
        return ExitCodes.EXIT_ABORT if self.quit else ExitCodes.EXIT_OK


def interactive() -> bool:
    """True when a question can actually be put to a human, and answered.

    Three conditions, all necessary: stdin is a tty (there is somebody typing — a pipe, a
    heredoc or `< /dev/null` is not), stdout is a terminal (the prompt would be visible), and
    the console is not muted by `--silent` (a quietable command in a pipeline must never block
    on a question nobody can see). The web shell satisfies all three: its stdin *is* a PTY.
    """
    return bool(sys.stdin.isatty() and console.is_interactive and not console.quiet)


def _require_interactive(what: str, hint: str) -> None:
    """Refuse a dialogue that cannot be shown, naming what to pass instead."""
    if not interactive():
        message = f'{what} needs an interactive shell'
        raise Abort(f'{message} — {hint}' if hint else message, rc=ExitCodes.EXIT_USAGE)


def _read(prompt: str, *, password: bool = False) -> str:
    """Read one line, turning the two ways a user leaves into an :class:`Abort`."""
    try:
        return str(console.input(prompt, password=password)).strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        raise Abort() from None


def _cue(*parts: str) -> str:
    """The prompt line: the affordances, then the one place the cursor sits."""
    return '  [muted]' + ' [accent.dim]·[/accent.dim] '.join(parts) + '[/muted] [accent]>[/accent] '


# ── in-command dialogues ────────────────────────────────────────────────────────────────

def confirm(question: str, *, default: bool = False, assume: bool | None = None) -> bool:
    """Ask a reversible yes/no question. Enter takes *default*.

    For anything a mistake would cost real work, use :func:`sure` instead — a question you can
    answer with a reflex Enter is not a safeguard.

    Args:
        question: What is about to happen, phrased as a question.
        default: The answer Enter gives. Defaults to False.
        assume: What to answer when there is nobody to ask. Defaults to None, which aborts
            rather than guessing — the safe reading for anything worth confirming.
    """
    if not interactive():
        if assume is None:
            raise Abort(f'{question} — needs an interactive shell to confirm',
                        rc=ExitCodes.EXIT_USAGE)
        return assume
    console.print(f'[primary]{question}[/primary]')
    answer = _read(_cue('y/n', f'Enter for {"yes" if default else "no"}'))
    return default if not answer else answer[:1].lower() == 'y'


def sure(question: str, *, phrase: str) -> bool:
    """Ask a question that must be answered by typing *phrase* exactly.

    The friction is the point: for a destructive, unrecoverable act — rotating the master key,
    replacing an identity — the user should have to read something before agreeing to it.

    Args:
        question: What is about to happen, and what it costs.
        phrase: The word the user must type. Make it name the act (`rekey`), not `yes`.
    """
    _require_interactive(question, 'it cannot be confirmed non-interactively')
    console.print(f'[warning]{question}[/warning]')
    answer = _read(_cue(f'type [accent]{phrase}[/accent] to confirm', 'Enter to cancel'))
    return answer.casefold() == phrase.casefold()


def pause(message: str = 'paused') -> None:
    """Wait for Enter. A no-op when there is nobody to wait for, never an error."""
    if not interactive():
        return
    console.print(f'[muted]{message}[/muted]')
    _read(_cue('Enter to continue'))


def text(question: str, *, default: str = '', validate: Callable[[str], str | None] | None = None,
         multiline: bool = False, secret_input: bool = False, allow_empty: bool = False) -> str:
    """Read a free-text answer, re-asking until *validate* is satisfied.

    Args:
        question: What to type.
        default: The value Enter gives. Defaults to '', which re-asks instead.
        validate: Returns an error message for a bad answer, or None to accept it. Defaults to
            None, which accepts anything non-empty.
        multiline: Read lines until a blank one, joining them. Defaults to False.
        secret_input: Hide what is typed. Defaults to False.
        allow_empty: Accept an empty answer instead of re-asking — for a question whose
            answer is genuinely optional, where Enter means "skip this". Defaults to False,
            because for most questions nothing typed is nothing said, not an answer.
    """
    _require_interactive(question, 'pass it as an argument')
    while True:
        console.print(f'[primary]{question}[/primary]')
        if multiline:
            console.print('  [muted]end with a blank line[/muted]')
            lines: list[str] = []
            while (line := _read('  [accent]|[/accent] ')) or not lines:
                if not line:
                    continue
                lines.append(line)
            answer = '\n'.join(lines)
        else:
            answer = _read(_cue(f'Enter for {default!r}') if default else '  [accent]>[/accent] ',
                           password=secret_input)
            answer = answer or default
        if not answer:
            if allow_empty:
                return ''
            console.print('  [warning]nothing typed[/warning]')
            continue
        if validate and (problem := validate(answer)):
            console.print(f'  [warning]{problem}[/warning]')
            continue
        return answer


def secret(question: str, *, confirm_twice: bool = False, hint: str = '') -> str:
    """Read a password without echoing it, optionally twice.

    Args:
        question: What password is wanted.
        confirm_twice: Ask again and require the two to match. Defaults to False.
        hint: How to supply it without a prompt (an environment variable), for the message
            shown when there is nobody to ask.
    """
    _require_interactive(question, hint)
    first = text(question, secret_input=True)
    if confirm_twice and text('Confirm it', secret_input=True) != first:
        raise Abort('the passwords do not match')
    return first


# ── choosing ────────────────────────────────────────────────────────────────────────────

def _menu(options: Sequence[Choice], *, marked: str = '') -> Table:
    """The numbered option table — the shared look of every menu in the shell."""
    table = Table(show_header=False, box=None, padding=(0, 2), pad_edge=True)
    table.add_column(style='accent', no_wrap=True, justify='right')
    table.add_column(style='accent.dim', no_wrap=True)
    table.add_column(style='cmd.help', overflow='fold')
    for index, option in enumerate(options, start=1):
        note = Text(option.description)
        if option.value == marked:
            note.append('  ← default', style='muted')
        table.add_row(str(index), option.text, note)
    return table


def _match(answer: str, options: Sequence[Choice]) -> Choice | None:
    """Resolve an answer against the options: a menu number, or a value/label typed out."""
    if answer.isdigit() and 1 <= int(answer) <= len(options):
        return options[int(answer) - 1]
    lowered = answer.casefold()
    for option in options:
        if lowered in (option.value.casefold(), option.text.casefold()):
            return option
    return None


def choose(question: str, options: Sequence[Choice], *, default: str = '', empty: str = '',
           strict: bool = True) -> str:
    """Ask for one of *options* and return its value.

    A short list renders as a numbered menu; above :data:`MENU_MAX` it becomes a search — type
    a term to narrow, then a number — because a menu nobody can read is not a menu. An empty
    *options* raises :class:`Abort`: nothing can be chosen, and saying so is more use than an
    empty list.

    Args:
        question: What is being chosen.
        options: The options, in the order to show them.
        default: The value Enter gives. Defaults to '', requiring an explicit answer.
        empty: The message when there is nothing to choose from.
        strict: Accept only a listed option. Defaults to True; False returns what was typed,
            for a set that is suggested rather than exhaustive.
    """
    if not options:
        raise Abort(empty or f'{question} — nothing to choose from', rc=ExitCodes.EXIT_ERROR)
    _require_interactive(question, 'pass the value as an argument')
    searching = len(options) > MENU_MAX
    shown: Sequence[Choice] = options[:MENU_MAX] if searching else options
    console.print(f'[primary]{question}[/primary]')
    while True:
        console.print(_menu(shown, marked=default))
        if searching and len(options) > len(shown):
            console.print(f'  [muted]… {len(options) - len(shown)} more — type a term to '
                          'narrow the list[/muted]')
        cues = [f'1-{len(shown)}']
        if searching:
            cues.append('a term to search')
        if default:
            cues.append(f'Enter for {default}')
        cues.append('q to quit')
        answer = _read(_cue(*cues))
        if answer in ('q', 'quit'):
            raise Abort()
        if not answer and default:
            return default
        if (picked := _match(answer, shown)) is not None:
            return picked.value
        if searching and answer:
            term = answer.casefold()
            matches = [o for o in options
                       if term in o.value.casefold() or term in o.text.casefold()
                       or term in o.description.casefold()]
            if not matches:
                console.print('  [warning]nothing matches[/warning]')
                continue
            shown = matches[:MENU_MAX]
            continue
        if not strict and answer:
            return answer
        console.print('  [warning]not one of the options[/warning]')


def select(question: str, candidates: Sequence[Choice], *, chosen: Iterable[str] = ()) -> list[str]:
    """Pick several of *candidates* — search, toggle by number, then finish.

    The multi-select counterpart of :func:`choose`, for a vocabulary too large to list: type a
    term to search, a result's number to toggle it, `sel` to review the selection, `done` to
    finish, `q` to abort.

    Args:
        question: What is being selected.
        candidates: Everything selectable.
        chosen: Values already selected, for re-editing a selection. Defaults to none.
    """
    if not candidates:
        raise Abort(f'{question} — nothing to select from', rc=ExitCodes.EXIT_ERROR)
    _require_interactive(question, 'pass the values as arguments')
    by_value = {candidate.value: candidate for candidate in candidates}
    selected: list[str] = [value for value in chosen if value in by_value]
    results: list[Choice] = []
    console.print(f'[primary]{question}[/primary]')
    console.print('  [muted]a term searches [accent.dim]·[/accent.dim] a number toggles '
                  '[accent.dim]·[/accent.dim] [accent]sel[/accent] review '
                  '[accent.dim]·[/accent.dim] [accent]done[/accent] '
                  '[accent.dim]·[/accent.dim] [accent]q[/accent] quit[/muted]')
    while True:
        answer = _read(_cue(f'{len(selected)} selected'))
        if answer in ('q', 'quit'):
            raise Abort()
        if answer == 'done':
            if selected:
                return selected
            console.print('  [warning]nothing selected yet[/warning]')
            continue
        if answer == 'sel':
            console.print('  [accent]selected:[/accent] ' + (', '.join(selected) or '[muted]none[/muted]'))
            continue
        if answer.isdigit():
            if not 1 <= int(answer) <= len(results):
                console.print('  [warning]no result with that number — search first[/warning]')
                continue
            value = results[int(answer) - 1].value
            if value in selected:
                selected.remove(value)
                console.print(f'  [muted]removed[/muted] {value}')
            else:
                selected.append(value)
                console.print(f'  [accent]added[/accent] {value}')
            continue
        if not answer:
            continue
        term = answer.casefold()
        matches = [c for c in candidates
                   if term in c.value.casefold() or term in c.text.casefold()
                   or term in c.description.casefold()]
        if not matches:
            console.print('  [muted]nothing matches[/muted]')
            continue
        results = matches[:MENU_MAX * 2]
        table = Table(show_header=False, box=None, padding=(0, 2), pad_edge=True)
        table.add_column(style='accent', no_wrap=True, justify='right')
        table.add_column(style='accent.dim', no_wrap=True)
        table.add_column(style='cmd.help', overflow='fold')
        for index, candidate in enumerate(results, start=1):
            mark = '[accent]✓[/accent]' if candidate.value in selected else ' '
            table.add_row(str(index), f'{mark} {candidate.text}', candidate.description)
        console.print(table)
        if len(matches) > len(results):
            console.print(f'  [muted]… {len(matches) - len(results)} more — refine the search[/muted]')


# ── walking a queue ─────────────────────────────────────────────────────────────────────

def walk(items: Sequence[Any], actions: dict[str, Action], *,
         render: Callable[[Any], Any], label: str = 'item') -> WalkResult:
    """Work through *items* one at a time, taking an action on each.

    The shared shape of every queue in the shell — open pull requests, invite requests, the
    staff message queue. Each item is rendered, then one keypress chooses its action; `q`
    stops the walk and makes the result an abort, so a chain gated on the command does not
    carry on as though the queue had been worked.

    Args:
        items: The queue, in the order to work it.
        actions: Key → :class:`Action`. `q` is added and must not be given.
        render: Turns one item into something printable — the panel or line shown before the
            prompt.
        label: What one item is called, for the counters. Defaults to 'item'.
    """
    if 'q' in actions:
        raise ValueError("'q' is the walk's own quit key")
    result = WalkResult()
    if not items:
        console.print(f'[muted]no {label}s[/muted]')
        return result
    _require_interactive(f'{len(items)} {label}(s)', 'there is nothing to walk non-interactively')
    keys = '/'.join([*actions, 'q'])
    legend = ' [accent.dim]·[/accent.dim] '.join(
        [f'[accent]{key}[/accent]{action.name[1:] if action.name[:1] == key else f" {action.name}"}'
         for key, action in actions.items()] + ['[accent]q[/accent]uit'])
    console.print(f'[accent]{len(items)}[/accent] {label}(s) — {legend}')
    for position, item in enumerate(items, start=1):
        console.print()
        console.print(render(item))
        answer = _read(_cue(keys, f'{position}/{len(items)}'))[:1].lower()
        if answer == 'q':
            result.quit = True
            break
        action = actions.get(answer)
        if action is None:
            console.print('  [warning]not an option — left as it is[/warning]')
            result.counts['untouched'] = result.counts.get('untouched', 0) + 1
            continue
        action.run(item)
        result.counts[action.name] = result.counts.get(action.name, 0) + 1
    summary = ' [accent.dim]·[/accent.dim] '.join(f'{count} {name}'
                                                  for name, count in result.counts.items())
    console.print(f'\n[muted]{summary or "nothing done"}'
                  f'{" — quit" if result.quit else ""}[/muted]')
    return result
