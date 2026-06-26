#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Lexer for shell v2: syntax-check a command block and normalise it.

`lex` turns a raw command block (the surface syntax of `docs/syntax.md`) into the
**canonical form** of §8 — a loop header over a brace group of guarded
statements — raising `LexError` on invalid syntax. The pipeline is:

    tokenise → parse (surface grammar, §9) → lower `&&`/`||` to guards (§5)
             → render canonical text (§8)

`is_complete` is the helper the reader uses to decide whether a partially typed
block needs another line (unbalanced braces or an open quote).
"""
from __future__ import annotations

__all__ = ['LexError', 'is_complete', 'lex']

import re
from dataclasses import dataclass

#: A user variable name (assignment target): lowercase, leading letter (§3).
_NAME_RE = re.compile(r'[a-z][a-z0-9_]*')

#: A complete variable reference — `{name}`, with an optional `.attr` path and
#: `:spec` (§2). Mirrors the name alternative of the interpreter's substitution
#: regex.
_REF_RE = re.compile(r'\{[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*(?::[^{}]*)?\}')

#: A lexer token: (kind, text, position-in-body).
_Token = tuple[str, str, int]


class LexError(SyntaxError):
    """A positioned syntax error, rendered with the offending line and a caret."""


# ---------------------------------------------------------------------------
# Surface-syntax AST (§9) and lowered canonical statements (§8)
# ---------------------------------------------------------------------------

@dataclass
class Stmt:
    """A leaf statement: an assignment (`target` set) or a bare command/expr."""
    target: str | None
    evaluation: str


@dataclass
class Group:
    """A `{ … }` group wrapping a sequence."""
    seq: Seq


@dataclass
class And:
    """`&&`-separated primaries (run the next only when the previous succeeds)."""
    items: list[Stmt | Group]


@dataclass
class Or:
    """`||`-separated and-expressions."""
    items: list[And]


@dataclass
class Seq:
    """`;`/newline-separated or-expressions."""
    items: list[Or]


@dataclass
class Leaf:
    """A canonical guarded statement: `guard: target = evaluation [|| on_error];`."""
    guard: str
    target: str
    evaluation: str
    on_error: str = 'ignore'


@dataclass
class GroupStmt:
    """A canonical guarded group: `guard: { … } [|| on_error];`."""
    guard: str
    body: list[Leaf | GroupStmt]
    on_error: str = 'ignore'


_Node = Stmt | Group | And | Or
_Canon = Leaf | GroupStmt


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------

def _err(message: str, text: str, pos: int) -> LexError:
    """Build a `LexError` pointing at *pos* within *text* (line + caret)."""
    pos = max(0, min(pos, len(text)))
    line_start = text.rfind('\n', 0, pos) + 1
    line_end = text.find('\n', pos)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    col = pos - line_start
    lineno = text.count('\n', 0, pos) + 1
    caret = ' ' * col + '^'
    return LexError(f'{message}\n  {line}\n  {caret}  (line {lineno}, col {col + 1})')


def _reference_end(text: str, pos: int) -> int | None:
    """Validate the variable reference opening at `text[pos]` (a non-group `{`).

    Return the index just past a complete `{name}` / `{name.attr}` /
    `{name:spec}` (name and attribute segments per the §3 convention
    `[a-z][a-z0-9_]*`); raise a positioned `LexError` for a malformed but
    *closed* reference (e.g. `{0problem}`, `{problem[0:1]}`); return `None` when
    no closing `}` is present yet, leaving the caller to treat it as an
    unterminated brace.
    """
    ref = _REF_RE.match(text, pos)
    if ref is not None:
        return ref.end()
    close = text.find('}', pos)
    if close != -1:
        raise _err(f'invalid variable reference {text[pos:close + 1]!r}: '
                   'expected {name}, {name.attr} or {name:spec}', text, pos)
    return None


def _validate_refs(text: str, start: int, end: int) -> None:
    """Reject a malformed `{name…}` reference within `text[start:end]`.

    Covers spans the tokeniser does not scan char-by-char — currently the loop
    header — so a bad reference there is caught at lex time too.
    """
    i, quote = start, ''
    while i < end:
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
        elif c == '{':
            if text[i:i + 2] == '{{':
                i += 2
                continue
            ref_end = _reference_end(text, i)
            if ref_end is not None and ref_end <= end:
                i = ref_end
                continue
        i += 1


# ---------------------------------------------------------------------------
# Low-level scanning (shared completeness check)
# ---------------------------------------------------------------------------

def _scan_state(text: str) -> tuple[int, bool]:
    """Return `(open_brace_depth, in_open_quote)` for *text*.

    Comments, escapes, and doubled braces (`{{` / `}}`) are ignored; structural
    and variable-reference braces are counted alike, since both must close for a
    block to be complete. (Only braces drive line continuation — `()` / `[]` may
    appear unbalanced in a command argument, so they are not counted.)
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
        if c == '#':
            nl = text.find('\n', i)
            if nl == -1:
                break
            i = nl
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
        i += 1
    return depth, bool(quote)


def is_complete(block: str) -> bool:
    """True when *block* needs no further input.

    A block is still open when braces are unbalanced, a quote is unterminated,
    it ends on a dangling `&&` / `||` (a right operand is awaited), or it is a
    `loop` header whose body has not been typed yet.
    """
    depth, in_quote = _scan_state(block)
    if depth > 0 or in_quote:
        return False
    code = block.rstrip()
    if code.endswith('&&') or code.endswith('||'):
        return False
    return not _loop_body_pending(block)


def _loop_body_pending(block: str) -> bool:
    """True when *block* opens a `loop` header whose body is not yet present."""
    i, n = 0, len(block)
    while i < n and block[i] in ' \t\r\n':
        i += 1
    after = block[i + 4] if i + 4 < n else ''
    if block[i:i + 4] != 'loop' or not (after == '' or after.isspace() or after == ':'):
        return False
    colon = _find_top_colon(block, i + 4)
    if colon is None:
        # No header ':' yet. Treat as still being typed *unless* a structural
        # `{ … }` body group is already present (and closed — balanced braces
        # were checked before this call): the lexer auto-fixes the missing ':'
        # at the group, so the block may submit (see _split_loop_header).
        return _find_group_brace(block, i + 4) is None
    return block[colon + 1:].strip() == ''


def _find_group_brace(text: str, start: int) -> int | None:
    """Index of the first top-level structural `{ … }` group opener, else None.

    A group brace is a `{` followed by whitespace, end-of-input, or `}` (the
    tokeniser's rule); this distinguishes it from a `{name}` substitution brace
    (followed immediately by a name character), so the two are not confused when
    judging whether a colon-less `loop` body is present (letting the block
    submit and the missing `:` be auto-fixed at the group) or merely unfinished.
    """
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
            nxt = text[i + 1] if i + 1 < n else ''
            if depth == 0 and (nxt == '' or nxt.isspace() or nxt == '}'):
                return i
            depth += 1
        elif c == '}':
            if text[i:i + 2] == '}}':
                i += 2
                continue
            depth -= 1
        i += 1
    return None


# ---------------------------------------------------------------------------
# Loop header
# ---------------------------------------------------------------------------

def _find_top_colon(text: str, start: int) -> int | None:
    """Index of the first top-level `:` at or after *start*, else None.

    Colons nested inside braces (`{…}`), brackets (`[…]`), or parentheses
    (`(…)`) are skipped, so a slice in the loop list — `loop {problems}[6:10:2]:`
    — does not have its header terminator misread as the `:` inside the slice.
    """
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
        elif c == '#' and depth == 0:
            nl = text.find('\n', i)
            if nl == -1:
                return None
            i = nl + 1
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
        elif c in '([':
            depth += 1
        elif c in ')]':
            depth -= 1
        elif c == ':' and depth == 0:
            return i
        i += 1
    return None


def _split_loop_header(block: str) -> tuple[str | None, str]:
    """Split a leading `loop <expr>:` header from *block*.

    Returns `(loop_expr_or_None, body)`. The loop keyword is recognised only at
    block start, followed by whitespace or `:`.

    A missing header `:` is **auto-fixed** when the body boundary is
    unambiguous — the body is a structural `{ … }` group, or starts on a new
    line — by splitting the header there. An inline body on the same line
    (`loop [1, 2] echo hi`) stays an error: the list expression cannot be told
    apart from the body without the `:`.
    """
    i, n = 0, len(block)
    while i < n and block[i] in ' \t\r\n':
        i += 1
    after = block[i + 4] if i + 4 < n else ''
    if block[i:i + 4] == 'loop' and (after == '' or after.isspace() or after == ':'):
        colon = _find_top_colon(block, i + 4)
        if colon is None:
            # Auto-fix: split at the earliest unambiguous body boundary — the
            # first structural `{ … }` group opener or the first newline.
            nl = block.find('\n', i + 4)
            boundaries = [p for p in (_find_group_brace(block, i + 4),
                                      nl if nl != -1 else None) if p is not None]
            split = min(boundaries, default=None)
            if split is None or not block[split:].strip():
                # No body to split off (or only blank lines follow) — point the
                # caret where the ':' belongs, at the header's end.
                raise _err("loop header is missing its ':' before the body",
                           block, split if split is not None else n)
            _validate_refs(block, i + 4, split)  # the header bypasses the tokeniser
            expr = block[i + 4:split].strip()
            return (expr or None), block[split:]
        _validate_refs(block, i + 4, colon)  # the header bypasses the tokeniser
        expr = block[i + 4:colon].strip()
        return (expr or None), block[colon + 1:]
    return None, block


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenize(body: str) -> list[_Token]:
    """Split *body* into structural tokens and statement chunks (§2)."""
    tokens: list[_Token] = []
    buf: list[str] = []
    buf_start = 0
    ref_depth = 0
    at_primary = True
    i, n = 0, len(body)

    def flush() -> None:
        nonlocal buf, ref_depth, at_primary
        text = ''.join(buf).strip()
        if text:
            tokens.append(('CHUNK', text, buf_start))
            at_primary = False
        buf = []
        ref_depth = 0

    def emit_semi(pos: int) -> None:
        if tokens and tokens[-1][0] not in ('SEMI', 'AND', 'OR', 'LBRACE'):
            tokens.append(('SEMI', ';', pos))

    while i < n:
        c = body[i]
        nxt = body[i + 1] if i + 1 < n else ''
        if c in '\'"':
            j = i + 1
            while j < n and body[j] != c:
                if c == '"' and body[j] == '\\':
                    j += 2
                    continue
                j += 1
            if j >= n:
                raise _err(f'unterminated {c} quote', body, i)
            if not buf:
                buf_start = i
            buf.append(body[i:j + 1])
            at_primary = False
            i = j + 1
            continue
        if c == '\\':
            if not buf:
                buf_start = i
            buf.append(body[i:i + 2])
            at_primary = False
            i += 2
            continue
        if c == '#' and ref_depth == 0:
            nl = body.find('\n', i)
            i = n if nl == -1 else nl
            continue
        if ref_depth == 0 and (c == '\n' or c == ';'):
            flush()
            emit_semi(i)
            at_primary = True
            i += 1
            continue
        if ref_depth == 0 and c == '&' and nxt == '&':
            flush()
            tokens.append(('AND', '&&', i))
            at_primary = True
            i += 2
            continue
        if ref_depth == 0 and c == '|' and nxt == '|':
            flush()
            tokens.append(('OR', '||', i))
            at_primary = True
            i += 2
            continue
        if c.isspace():
            if buf:
                buf.append(c)
            i += 1
            continue
        if c == '{':
            if nxt == '{':
                if not buf:
                    buf_start = i
                buf.append('{{')
                at_primary = False
                i += 2
                continue
            if at_primary and not buf and (nxt == '' or nxt.isspace() or nxt == '}'):
                tokens.append(('LBRACE', '{', i))
                at_primary = True
                i += 1
                continue
            # A non-group `{` opens a variable reference; it must be a complete
            # `{name}` / `{name:spec}` with a convention-valid name. Consume a
            # valid one as a unit; reject a malformed one (`{0problem}`,
            # `{problem[0:1]}`, `{1,2,3}`) — `{…}` is a reference, not a set/dict
            # literal, and an index/slice belongs *outside* it: `{problem}[0:1]`.
            ref_end = _reference_end(body, i)
            if ref_end is not None:
                if not buf:
                    buf_start = i
                buf.append(body[i:ref_end])
                at_primary = False
                i = ref_end
                continue
            # no closing `}` yet — fall through to the unterminated handling
            if not buf:
                buf_start = i
            ref_depth += 1
            buf.append('{')
            at_primary = False
            i += 1
            continue
        if c == '}':
            if nxt == '}':
                buf.append('}}')
                at_primary = False
                i += 2
                continue
            if ref_depth > 0:
                ref_depth -= 1
                buf.append('}')
                i += 1
                continue
            flush()
            tokens.append(('RBRACE', '}', i))
            at_primary = False
            i += 1
            continue
        if not buf:
            buf_start = i
        buf.append(c)
        at_primary = False
        i += 1

    if ref_depth > 0:
        raise _err("unterminated '{' in expression", body, buf_start)
    flush()
    return tokens


# ---------------------------------------------------------------------------
# Parser (surface grammar, §9)
# ---------------------------------------------------------------------------

def _classify(chunk: str, pos: int, body: str) -> Stmt:
    """Classify a chunk as an assignment (`name = …`) or a bare statement (§4)."""
    eq = _find_assign_eq(chunk)
    if eq is not None:
        name = chunk[:eq].strip()
        value = chunk[eq + 1:].strip()
        if _NAME_RE.fullmatch(name):
            if not value:
                raise _err(f'assignment to {name!r} has no value', body, pos)
            return Stmt(name, value)
    return Stmt(None, chunk)


def _find_assign_eq(text: str) -> int | None:
    """Index of a top-level lone `=` (assignment), distinct from `==`/`<=`/…."""
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
        elif c == '=' and depth == 0:
            prev = text[i - 1] if i > 0 else ''
            nxt = text[i + 1] if i + 1 < n else ''
            if prev not in '=!<>' and nxt != '=':
                return i
        i += 1
    return None


class _Parser:
    """Recursive-descent parser over the token stream (§9)."""

    def __init__(self, tokens: list[_Token], body: str) -> None:
        self._toks = tokens
        self._body = body
        self._pos = 0

    def _peek(self) -> _Token:
        if self._pos < len(self._toks):
            return self._toks[self._pos]
        return ('EOF', '', len(self._body))

    def _advance(self) -> _Token:
        tok = self._peek()
        self._pos += 1
        return tok

    @staticmethod
    def _desc(tok: _Token) -> str:
        labels = {'AND': "'&&'", 'OR': "'||'", 'SEMI': "';'", 'LBRACE': "'{'",
                  'RBRACE': "'}'", 'EOF': 'end of input'}
        return labels.get(tok[0], repr(tok[1]))

    def parse(self) -> Seq:
        """Parse the whole token stream into a `Seq`, erroring on trailing tokens."""
        seq = self._sequence()
        if self._peek()[0] != 'EOF':
            tok = self._peek()
            raise _err(f'unexpected {self._desc(tok)}', self._body, tok[2])
        return seq

    def _sequence(self) -> Seq:
        """Parse a `;`-separated sequence of `||` expressions (empty statements collapsed)."""
        items = [self._or()]
        while self._peek()[0] == 'SEMI':
            while self._peek()[0] == 'SEMI':
                self._advance()
            if self._peek()[0] in ('EOF', 'RBRACE'):
                break
            items.append(self._or())
        return Seq(items)

    def _or(self) -> Or:
        """Parse one or more `&&` expressions separated by `||`."""
        items = [self._and()]
        while self._peek()[0] == 'OR':
            self._advance()
            items.append(self._and())
        return Or(items)

    def _and(self) -> And:
        """Parse one or more primaries (statements or groups) separated by `&&`."""
        items: list[Stmt | Group] = [self._primary()]
        while self._peek()[0] == 'AND':
            self._advance()
            items.append(self._primary())
        return And(items)

    def _primary(self) -> Stmt | Group:
        """Parse a single statement (CHUNK) or a `{ … }` group."""
        tok = self._peek()
        if tok[0] == 'LBRACE':
            self._advance()
            seq = self._sequence()
            if self._peek()[0] != 'RBRACE':
                raise _err("expected '}' to close the group", self._body, self._peek()[2])
            self._advance()
            return Group(seq)
        if tok[0] == 'CHUNK':
            self._advance()
            return _classify(tok[1], tok[2], self._body)
        raise _err(f'expected a statement but found {self._desc(tok)}', self._body, tok[2])


# ---------------------------------------------------------------------------
# Lowering `&&`/`||` to guards (§5) and rendering canonical form (§8)
# ---------------------------------------------------------------------------

def _lower_seq(seq: Seq) -> list[_Canon]:
    """Lower every `||` expression in a sequence to a flat list of canonical statements."""
    out: list[_Canon] = []
    for or_expr in seq.items:
        out += _lower(or_expr, 'True')
    return out


def _lower(node: _Node, guard: str) -> list[_Canon]:
    """Lower *node* to canonical statements that run it as a unit, gated by *guard*."""
    if isinstance(node, Stmt):
        return [Leaf(guard, node.target or '_', node.evaluation)]
    if isinstance(node, Group):
        inner = _lower_seq(node.seq)
        if not inner:
            return []
        return inner if guard == 'True' else [GroupStmt(guard, inner)]
    if isinstance(node, And):
        if len(node.items) == 1:
            return _lower(node.items[0], guard)
        chain: list[_Canon] = []
        for k, primary in enumerate(node.items):
            chain += _lower(primary, 'True' if k == 0 else '{rcode} == 0')
        return chain if guard == 'True' else [GroupStmt(guard, chain)]
    # Or — a trailing `|| continue` / `|| break` folds into the operand's on_error.
    items = node.items
    on_error = ''
    if len(items) > 1:
        kw = _flow_kw(items[-1])
        if kw in ('continue', 'break'):
            on_error, items = kw, items[:-1]
    if len(items) == 1:
        result = _lower(items[0], guard)
    else:
        chain = []
        for k, and_expr in enumerate(items):
            chain += _lower(and_expr, 'True' if k == 0 else '{rcode} != 0')
        result = chain if guard == 'True' else [GroupStmt(guard, chain)]
    return _attach_on_error(result, guard, on_error) if on_error else result


def _flow_kw(node: And) -> str | None:
    """Return `continue`/`break` if *node* is a lone such flow-control statement."""
    if len(node.items) == 1 and isinstance(node.items[0], Stmt):
        stmt = node.items[0]
        if stmt.target is None and stmt.evaluation in ('continue', 'break'):
            return stmt.evaluation
    return None


def _attach_on_error(result: list[_Canon], guard: str, on_error: str) -> list[_Canon]:
    """Attach *on_error* to a single statement, or wrap a multi-statement body."""
    if len(result) == 1:
        result[0].on_error = on_error
        return result
    return [GroupStmt(guard, result, on_error)]


def _render(loop_expr: str | None, stmts: list[_Canon]) -> str:
    """Render the canonical guarded form (§8): a loop header and a braced body."""
    header = f'{loop_expr}:' if loop_expr else 'None:'
    return '\n'.join([header, '{', *_render_body(stmts, 1), '}'])


def _render_body(stmts: list[_Canon], level: int) -> list[str]:
    """Render canonical statements as indented `guard: target = eval || on_error;` lines."""
    indent = '    ' * level
    out: list[str] = []
    for stmt in stmts:
        clause = '' if stmt.on_error == 'ignore' else f' || {stmt.on_error}'
        if isinstance(stmt, Leaf):
            out.append(f'{indent}{stmt.guard}: {stmt.target} = {stmt.evaluation}{clause};')
        else:
            out.append(f'{indent}{stmt.guard}: {{')
            out += _render_body(stmt.body, level + 1)
            out.append(f'{indent}}}{clause};')
    return out


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def lex(block: str) -> str:
    """Syntax-check *block* and return its canonical form (§8).

    Raises `LexError` (a `SyntaxError`) on invalid or empty input.
    """
    loop_expr, body = _split_loop_header(block)
    tokens = _tokenize(body)
    if not tokens:
        raise LexError('empty command block')
    stmts = _lower_seq(_Parser(tokens, body).parse())
    if not stmts:
        raise LexError('empty command block')
    return _render(loop_expr, stmts)
