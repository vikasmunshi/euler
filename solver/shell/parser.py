#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Parser for shell v2: canonical form (the lexer's output) → typed statements.

`parse` consumes the canonical string of `docs/syntax.md` §8 and returns

    (loop, [Statement(guard, target, evaluation, on_error), …])

where every guard and evaluation is **classified** into one of four kinds so the
interpreter knows how to run it:

* `Variable`  — a lone `{name}` reference
* `Command`   — first token is a known command name (a stub set, for now)
* `Flow`      — a `continue` / `break` / `exit` control word
* `Literal`   — any other value expression (it may still contain `{…}` refs)

Groups nest recursively: a group statement's `evaluation` is a `Block` (a list of
`Statement`s). Variable substitution itself is deferred to the interpreter; the
parser only marks where variables and commands are.
"""
from __future__ import annotations

__all__ = ['Block', 'Command', 'Eval', 'Flow', 'Literal', 'OnError', 'ParserError',
           'Statement', 'Variable', 'classify', 'dump', 'parse', 'set_commands']

import re
from dataclasses import dataclass
from enum import Enum
from typing import Generator, Iterable

#: Known command names used to classify an evaluation as a `Command`. Defaults
#: to a stub set for standalone use; the shell replaces it with the live command
#: registry's names via :func:`set_commands`.
COMMANDS: frozenset[str] = frozenset({
    'init', 'reinit', 'reset', 'stack', 'ls', 'eval', 'benchmark', 'lint',
    'echo', 'clear', 'help', 'find', 'loop',
})


def set_commands(names: Iterable[str]) -> None:
    """Replace the command set used for classification (e.g. registry names)."""
    global COMMANDS
    COMMANDS = frozenset(names)


#: A lone variable reference: a single `{…}` with no nested braces.
_LONE_VAR = re.compile(r'\{[^{}]+\}')

#: A command-like leading token: lowercase word (the form a command name takes).
_CMD_NAME = re.compile(r'[a-z][a-z0-9_-]*')


class ParserError(SyntaxError):
    """Raised on malformed canonical input (should not happen for lexer output)."""


# ---------------------------------------------------------------------------
# Classified evaluations and statements
# ---------------------------------------------------------------------------

@dataclass
class Variable:
    """A lone `{name}` reference resolved from the variable store."""
    text: str


@dataclass
class Command:
    """A command invocation: a registered `name` plus its raw argument string."""
    name: str
    args: str


@dataclass
class Literal:
    """A value expression (literals and any embedded `{…}` variable references)."""
    text: str


@dataclass
class Flow:
    """A flow-control word: `continue`, `break`, or `exit`."""
    kind: str


@dataclass
class Block:
    """A nested group: a sub-sequence of statements."""
    stmts: list[Statement]


Eval = Variable | Command | Literal | Flow | Block


class OnError(Enum):
    """What to do when a statement's evaluation fails (non-zero `rcode`)."""
    IGNORE = 'ignore'
    CONTINUE = 'continue'
    BREAK = 'break'


@dataclass
class Statement:
    """One canonical statement: `guard: target = evaluation [|| on_error]`."""
    guard: Eval
    target: str | None
    evaluation: Eval
    on_error: OnError


# ---------------------------------------------------------------------------
# Top-level scanning (depth/quote aware over the canonical text)
# ---------------------------------------------------------------------------

def _scan_top(text: str) -> Generator[tuple[int, str], None, None]:
    """Yield `(index, char)` for each char at depth 0, outside quotes.

    Depth counts braces (`{…}`), brackets (`[…]`), and parentheses (`(…)`) alike,
    so a `:` inside a slice (`{problems}[6:10:2]`) or a `,`/`;` inside a literal
    is not mistaken for a top-level header/guard/statement separator.
    """
    i, n, depth, quote = 0, len(text), 0, ''
    while i < n:
        c = text[i]
        if quote:
            if c == '\\' and quote == '"':
                i += 2
                continue
            if c == quote:
                quote = ''
            i += 1
            continue
        if c in '\'"':
            quote = c
            i += 1
            continue
        if c == '\\':
            i += 2
            continue
        if c == '{':
            if text[i:i + 2] == '{{':
                i += 2
                continue
            depth += 1
            i += 1
            continue
        if c == '}':
            if text[i:i + 2] == '}}':
                i += 2
                continue
            depth -= 1
            i += 1
            continue
        if c in '([':
            depth += 1
            i += 1
            continue
        if c in ')]':
            depth -= 1
            i += 1
            continue
        if depth == 0:
            yield i, c
        i += 1


def _first_top(text: str, char: str) -> int | None:
    for i, c in _scan_top(text):
        if c == char:
            return i
    return None


def _extract_braces(text: str, start: int) -> tuple[str, int]:
    """Given `text[start] == '{'`, return `(inner_text, index_after_close)`."""
    i, n, depth, quote = start, len(text), 0, ''
    while i < n:
        c = text[i]
        if quote:
            if c == '\\' and quote == '"':
                i += 2
                continue
            if c == quote:
                quote = ''
            i += 1
            continue
        if c in '\'"':
            quote = c
        elif c == '\\':
            i += 2
            continue
        elif c == '{':
            if text[i:i + 2] == '{{':
                i += 2
                continue
            depth += 1
        elif c == '}':
            if text[i:i + 2] == '}}':
                i += 2
                continue
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise ParserError('unbalanced braces in canonical form')


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify(text: str) -> Eval:
    """Classify an evaluation/guard string into its typed node."""
    t = text.strip()
    if t in ('continue', 'break', 'exit'):
        return Flow(t)
    # Sigil commands: '!' (shell passthrough) and '?' (help) may abut their
    # argument ('!ls', '?eval') — neither is ever valid at the start of a value
    # expression — so split the leading sigil into the command name.
    if t[:1] in ('!', '?'):
        return Command(t[0], t[1:].strip())
    head = t.split(None, 1)[0] if t else ''
    if head in COMMANDS:
        return Command(head, t[len(head):].strip())
    if _LONE_VAR.fullmatch(t):
        return Variable(t)
    # A command-like leading word *with arguments* that is not a registered
    # command is almost certainly a mistyped command (value expressions reference
    # names as `{name}`, never as bare words). Classify it as a Command so the
    # runner reports a clear "unknown command: …" instead of the evaluator's
    # opaque "invalid syntax".
    rest = t[len(head):].strip()
    if rest and _CMD_NAME.fullmatch(head):
        return Command(head, rest)
    return Literal(t)


# ---------------------------------------------------------------------------
# Statement / body parsing
# ---------------------------------------------------------------------------

def _split_semis(body: str) -> list[str]:
    out, start = [], 0
    for i, c in _scan_top(body):
        if c == ';':
            out.append(body[start:i])
            start = i + 1
    if body[start:].strip():
        out.append(body[start:])
    pieces: list[str] = []
    for piece in out:
        piece = piece.strip()
        if not piece:
            continue
        # A malformed statement (e.g. an unbalanced `(`) can hide its canonical
        # `;` terminator from the top-level split; strip it so it never leaks
        # into the leaf and the real error (the unclosed bracket) is reported.
        if piece.endswith(';'):
            piece = piece[:-1].rstrip()
        pieces.append(piece)
    return pieces


def _split_on_error(rest: str) -> tuple[str, OnError]:
    """Split a trailing top-level `|| continue` / `|| break` clause off *rest*."""
    items = list(_scan_top(rest))
    for k in range(len(items) - 1):
        i, c = items[k]
        j, d = items[k + 1]
        if c == '|' and d == '|' and j == i + 1:
            clause = rest[i + 2:].strip()
            if clause == 'continue':
                return rest[:i], OnError.CONTINUE
            if clause == 'break':
                return rest[:i], OnError.BREAK
            raise ParserError(f'invalid on-error clause: {clause!r}')
    return rest, OnError.IGNORE


def _split_assign(rest: str) -> tuple[str, str] | None:
    """Split a leaf on its top-level lone `=` into `(target, evaluation)`."""
    for i, c in _scan_top(rest):
        if c == '=':
            prev = rest[i - 1] if i > 0 else ''
            nxt = rest[i + 1] if i + 1 < len(rest) else ''
            if prev not in '=!<>' and nxt != '=':
                return rest[:i].strip(), rest[i + 1:].strip()
    return None


def _parse_statement(stmt: str) -> Statement:
    colon = _first_top(stmt, ':')
    if colon is None:
        raise ParserError(f'statement missing guard colon: {stmt!r}')
    guard = classify(stmt[:colon].strip())
    rest, on_error = _split_on_error(stmt[colon + 1:].strip())
    rest = rest.strip()
    if rest.startswith('{'):
        inner, end = _extract_braces(rest, 0)
        if rest[end:].strip():
            raise ParserError(f'unexpected text after group: {rest[end:].strip()!r}')
        return Statement(guard, None, Block(_parse_body(inner)), on_error)
    assign = _split_assign(rest)
    if assign is None:
        raise ParserError(f'statement missing target assignment: {stmt!r}')
    target, evaluation = assign
    return Statement(guard, None if target == '_' else target, classify(evaluation), on_error)


def _parse_body(body: str) -> list[Statement]:
    return [_parse_statement(piece.strip()) for piece in _split_semis(body)]


def parse(canonical: str) -> tuple[Eval | None, list[Statement]]:
    """Parse the lexer's canonical form into `(loop, statements)`."""
    colon = _first_top(canonical, ':')
    if colon is None:
        raise ParserError('canonical form missing header colon')
    header = canonical[:colon].strip()
    rest = canonical[colon + 1:]
    brace = rest.find('{')
    if brace == -1:
        raise ParserError('canonical form missing block')
    body, _ = _extract_braces(rest, brace)
    loop = None if header == 'None' else classify(header)
    return loop, _parse_body(body)


# ---------------------------------------------------------------------------
# Readable dump (for the launch test harness)
# ---------------------------------------------------------------------------

def _fmt(node: Eval) -> str:
    if isinstance(node, Variable):
        return f'var {node.text}'
    if isinstance(node, Command):
        return f'cmd {node.name}({node.args})' if node.args else f'cmd {node.name}'
    if isinstance(node, Literal):
        return f'lit {node.text!r}'
    if isinstance(node, Flow):
        return f'flow {node.kind}'
    return 'block'


def dump(loop: Eval | None, stmts: list[Statement]) -> str:
    """Render the parsed structure as indented text for inspection."""
    head = _fmt(loop) if loop is not None else 'None'
    return '\n'.join([f'loop: {head}', *_dump_stmts(stmts, 0)])


def _dump_stmts(stmts: list[Statement], level: int) -> list[str]:
    indent = '  ' * level
    out: list[str] = []
    for s in stmts:
        target = s.target if s.target else '_'
        suffix = '' if s.on_error is OnError.IGNORE else f'  (on_error={s.on_error.value})'
        if isinstance(s.evaluation, Block):
            out.append(f'{indent}if {_fmt(s.guard)} -> {target} = {{{suffix}')
            out += _dump_stmts(s.evaluation.stmts, level + 1)
            out.append(f'{indent}}}')
        else:
            out.append(f'{indent}if {_fmt(s.guard)} -> {target} = {_fmt(s.evaluation)}{suffix}')
    return out
