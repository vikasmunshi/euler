#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Interpreter for shell v2: execute the parser's statements.

`run` takes the parser output `(loop, statements)` and executes it against the
`variables` store, returning the final `rcode`. Per statement it:

1. evaluates the **guard** (skip the statement, leaving `rcode`, if falsy);
2. evaluates the **evaluation** — a command (via an injectable runner), a
   flow-control word, or a value expression — yielding a value and an `rcode`;
3. assigns the value to the **target** (unless `_`);
4. on failure (`rcode != 0`) applies **on_error**: continue / break the loop.

Variable substitution of `{name}` happens here (not in `variables.py`): for
expressions, literal-safe values become `repr` literals for the safe evaluator
while any other value (e.g. a `Problem`) is bound into the evaluator's namespace;
command lines use `shlex.quote(str(...))`.
"""
from __future__ import annotations

__all__ = ['CommandRunner', 'execute']

import ast
import math
import operator
import re
import shlex
from typing import Any, Callable

from rich.text import Text

from solver.shell.parser import Block, Command, Eval, Flow, Literal, OnError, Statement, Variable
from solver.shell.tty import console
from solver.shell.variables import variables

#: Runs a command by name with its tokenised args, returning a Unix exit code.
CommandRunner = Callable[[str, list[str]], int]


# ---------------------------------------------------------------------------
# Control-flow signals
# ---------------------------------------------------------------------------

class _Break(Exception):
    """Raised by `break` (and `|| break`) to stop the enclosing loop."""


class _Continue(Exception):
    """Raised by `continue` (and `|| continue`) to skip to the next loop value."""


class _ExprSyntaxError(ValueError):
    """A Python syntax error in a substituted expression.

    Carries the offending (post-substitution) text and the 1-based column so the
    interpreter can render it with a caret, matching the lexer/parser style.
    """

    def __init__(self, message: str, text: str, offset: int) -> None:
        super().__init__(message)
        self.text = text
        self.offset = offset


# ---------------------------------------------------------------------------
# Variable substitution
# ---------------------------------------------------------------------------

#: A `{name}` / `{name.attr}` / `{name:spec}` reference, or a `{{` / `}}`
#: literal brace.
_SUBST_RE = re.compile(r'(?P<lb>\{\{)|(?P<rb>\}\})|'
                       r'\{(?P<name>[a-z][a-z0-9_]*)(?P<attrs>(?:\.[a-z][a-z0-9_]*)*)'
                       r'(?::(?P<spec>[^{}]*))?\}')


def _substitute(text: str, render: Callable[[Any, str | None], str]) -> str:
    """Replace every `{name}` in *text* with its store value via *render*."""

    def repl(match: re.Match[str]) -> str:
        if match.group('lb'):
            return '{'
        if match.group('rb'):
            return '}'
        name = match.group('name')
        try:
            value = variables[name]
        except KeyError:
            raise NameError(f'undefined variable: {name}') from None
        if callable(value):
            value = value()
        path = name
        for attr in match.group('attrs').split('.')[1:]:
            path = f'{path}.{attr}'
            try:
                value = getattr(value, attr)
            except AttributeError:
                raise AttributeError(f'undefined attribute: {path}') from None
        return render(value, match.group('spec'))

    return _SUBST_RE.sub(repl, text)


def _is_literal_safe(value: Any) -> bool:
    """True when `repr(value)` round-trips to an equivalent literal.

    Such values can be substituted into the expression text directly; anything
    else (e.g. a `Problem` NamedTuple, whose `repr` is a constructor call, or a
    non-finite float, whose `repr` is the bare name `nan`/`inf`) is instead bound
    into the evaluator's namespace under a placeholder name.
    """
    # Exact-type checks, not isinstance: a subclass (a `Problem` NamedTuple is a
    # `tuple`; an `IntEnum` is an `int`) does not share its base's literal repr.
    kind = type(value)
    if value is None or kind in (bool, int, str, bytes):
        return True
    if kind is float:
        return math.isfinite(value)
    if kind is complex:
        return math.isfinite(value.real) and math.isfinite(value.imag)
    if kind in (list, tuple, set, frozenset):
        return all(_is_literal_safe(v) for v in value)
    if kind is dict:
        return all(_is_literal_safe(k) and _is_literal_safe(v) for k, v in value.items())
    return False


def _render_cmd(value: Any, spec: str | None) -> str:
    """Render a value as a single shell-safe command-line token."""
    return shlex.quote(format(value, spec) if spec else str(value))


# ---------------------------------------------------------------------------
# Safe expression evaluator (substitute-then-eval; no calls / attribute access)
# ---------------------------------------------------------------------------

_CMP_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
    ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}
_BIN_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARY_OPS: dict[type, Callable[[Any], Any]] = {
    ast.Not: operator.not_, ast.USub: operator.neg, ast.UAdd: operator.pos,
}

#: Whitelisted builtins callable from an expression. All are pure data functions
#: with no side effects; `range`/`reversed` materialise a list so the result is
#: an indexable, repr-friendly value. A call is allowed only when its callee is a
#: bare name in this map — never an attribute or a substituted value — so the
#: evaluator stays sandboxed (no attribute access, no arbitrary callables).
_FUNCTIONS: dict[str, Callable[..., Any]] = {
    'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict, 'divmod': divmod,
    'float': float, 'frozenset': frozenset, 'int': int, 'len': len, 'list': list,
    'max': max, 'min': min, 'range': lambda *a: list(range(*a)),
    'reversed': lambda x: list(reversed(x)), 'round': round, 'set': set, 'sorted': sorted,
    'str': str, 'sum': sum, 'tuple': tuple,
}


def _eval_node(node: ast.AST, namespace: dict[str, Any]) -> Any:
    """Recursively evaluate a whitelisted AST node against *namespace*.

    Supports constants, names (resolved from *namespace*), boolean/unary/binary
    operators, comparisons (including chains), list/tuple/set displays,
    subscripts and slices, and calls to the sandboxed `_FUNCTIONS` only. Any other
    node — or an undefined name, unsupported operator, or disallowed call — raises
    `ValueError`, keeping the evaluator free of attribute access and arbitrary
    callables.
    """
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, namespace)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in namespace:
            return namespace[node.id]
        raise ValueError(f'undefined name: {node.id}')
    if isinstance(node, ast.BoolOp):
        values = node.values
        if isinstance(node.op, ast.And):
            result: Any = True
            for sub in values:
                result = _eval_node(sub, namespace)
                if not result:
                    return result
            return result
        result = False
        for sub in values:
            result = _eval_node(sub, namespace)
            if result:
                return result
        return result
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f'unsupported unary operator: {type(node.op).__name__}')
        return op(_eval_node(node.operand, namespace))
    if isinstance(node, ast.BinOp):
        binop = _BIN_OPS.get(type(node.op))
        if binop is None:
            raise ValueError(f'unsupported operator: {type(node.op).__name__}')
        return binop(_eval_node(node.left, namespace), _eval_node(node.right, namespace))
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, namespace)
        for op_node, comparator in zip(node.ops, node.comparators):
            cmp = _CMP_OPS.get(type(op_node))
            if cmp is None:
                raise ValueError(f'unsupported comparison: {type(op_node).__name__}')
            right = _eval_node(comparator, namespace)
            if not cmp(left, right):
                return False
            left = right
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [_eval_node(elt, namespace) for elt in node.elts]
    if isinstance(node, ast.Subscript):
        container = _eval_node(node.value, namespace)
        key = _eval_node(node.slice, namespace)
        try:
            return container[key]
        except (TypeError, KeyError, IndexError) as exc:
            raise ValueError(f'invalid subscript: {exc}') from exc
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCTIONS:
            name = node.func.id if isinstance(node.func, ast.Name) else type(node.func).__name__
            raise ValueError(f'unsupported function: {name}')
        if any(isinstance(arg, ast.Starred) for arg in node.args):
            raise ValueError(f'unsupported call: *args in {node.func.id}()')
        args = [_eval_node(arg, namespace) for arg in node.args]
        kwargs: dict[str, Any] = {}
        for kw in node.keywords:
            if kw.arg is None:
                raise ValueError(f'unsupported call: **kwargs in {node.func.id}()')
            kwargs[kw.arg] = _eval_node(kw.value, namespace)
        try:
            return _FUNCTIONS[node.func.id](*args, **kwargs)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'{node.func.id}(): {exc}') from exc
    if isinstance(node, ast.Slice):
        lower = None if node.lower is None else _eval_node(node.lower, namespace)
        upper = None if node.upper is None else _eval_node(node.upper, namespace)
        step = None if node.step is None else _eval_node(node.step, namespace)
        return slice(lower, upper, step)
    raise ValueError(f'unsupported expression: {type(node).__name__}')


def _eval_expr(text: str) -> Any:
    """Substitute defined names in *text*, then safely evaluate it.

    Literal-safe values are substituted as their `repr` (so the safe evaluator
    sees a literal); any other value (e.g. a `Problem`) is bound under a fresh
    `_subst_N` placeholder name and resolved during evaluation, so opaque objects
    survive a `{name}` reference instead of being re-parsed as a call.
    """
    namespace: dict[str, Any] = {}

    def render(value: Any, spec: str | None) -> str:
        if spec is not None:
            return repr(format(value, spec))
        if _is_literal_safe(value):
            return repr(value)
        placeholder = f'_subst_{len(namespace)}'
        namespace[placeholder] = value
        return placeholder

    expr = _substitute(text, render).strip()
    if not expr:
        raise ValueError('empty expression')
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError as exc:
        raise _ExprSyntaxError(exc.msg or 'invalid syntax', expr, exc.offset or 1) from exc
    return _eval_node(tree, namespace)


# ---------------------------------------------------------------------------
# Console echo (results, assignments, errors)
# ---------------------------------------------------------------------------

def _print_error(message: str) -> None:
    """Print *message* to the console prefixed with a styled `error:` label."""
    text = Text('error: ', style='error')
    text.append(message)
    console.print(text)


def _print_syntax_error(exc: _ExprSyntaxError) -> None:
    """Render an expression syntax error with the offending text and a `^` caret,
    matching the positioned style of the lexer/parser errors."""
    col = min(max(exc.offset, 1), len(exc.text) + 1)
    head = Text('syntax error: ', style='error')
    head.append(str(exc), style='error')
    located = Text(f'  {exc.text}\n', style='muted')
    located.append('  ' + ' ' * (col - 1) + '^', style='warning')
    located.append(f'  (col {col})', style='muted')
    console.print(head)
    console.print(located)


def _echo_command(name: str, args: list[str], rcode: int) -> None:
    """Echo a run command and its resulting exit code as `name args → rcode`."""
    text = Text(name if not args else f'{name} {" ".join(args)}', style='muted')
    text.append(' → ', style='accent.dim')
    text.append(str(rcode))
    console.print(text)


def _echo_assignment(target: str, value: Any) -> None:
    """Echo an assignment as `target = repr(value)`."""
    text = Text(target, style='muted')
    text.append(' = ', style='accent.dim')
    text.append(repr(value))
    console.print(text)


def _echo_value(var: str, value: Any) -> None:
    """Echo a bare value expression as `var → repr(value)`."""
    text = Text(f'{var} → ', style='accent.dim')
    text.append(repr(value))
    console.print(text)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _evaluate(node: Eval, command: CommandRunner) -> tuple[Any, int]:
    """Evaluate *node*, returning `(value, rcode)`; flow words raise signals."""
    if isinstance(node, Flow):
        if node.kind == 'continue':
            raise _Continue
        if node.kind == 'break':
            raise _Break
        raise SystemExit(int(variables['rcode']))
    if isinstance(node, Command):
        args = shlex.split(_substitute(node.args, _render_cmd))
        rcode = command(node.name, args)
        _echo_command(node.name, args, rcode)
        return rcode, rcode
    if isinstance(node, Block):
        _exec_block(node.stmts, command)
        return None, variables.rcode
    # Variable or Literal -> value expression
    value = _eval_expr(node.text)
    return value, 0 if value else 1


def _eval_guard(guard: Eval) -> Any:
    """Evaluate a statement's guard expression to a truthy/falsy value.

    A guard is always a `Variable` or `Literal` (the lexer guarantees this); any
    other node is a programming error and raises `ValueError`.
    """
    if isinstance(guard, (Variable, Literal)):
        return _eval_expr(guard.text)
    raise ValueError(f'invalid guard: {guard!r}')


def _exec_statement(stmt: Statement, command: CommandRunner) -> None:
    """Execute one statement: guard, evaluate, assign, then apply on-error flow.

    Skips the statement (leaving `rcode` unchanged) when its guard is falsy.
    Otherwise evaluates it, records the resulting `rcode`, assigns the value to
    `stmt.target` (or echoes a bare value), and — on a non-zero `rcode` — raises
    `_Continue`/`_Break` per `stmt.on_error`. Expression and runtime errors are
    reported to the console and set `rcode` to 1; flow-control signals propagate.
    """
    if not _eval_guard(stmt.guard):
        return
    try:
        value, rcode = _evaluate(stmt.evaluation, command)
    except (_Break, _Continue, SystemExit, KeyboardInterrupt):
        raise
    except _ExprSyntaxError as exc:
        _print_syntax_error(exc)
        variables.rcode = rcode = 1
    except Exception as exc:
        _print_error(str(exc))
        variables.rcode = rcode = 1
    else:
        variables.rcode = rcode
        if stmt.target is not None:
            try:
                variables[stmt.target] = value
            except KeyError as exc:
                _print_error(str(exc))
                variables.rcode = rcode = 1
            else:
                _echo_assignment(stmt.target, value)
        elif isinstance(stmt.evaluation, (Variable, Literal)):
            _echo_value(stmt.evaluation.text, value)
    if rcode != 0:
        if stmt.on_error is OnError.CONTINUE:
            raise _Continue
        if stmt.on_error is OnError.BREAK:
            raise _Break


def _exec_block(stmts: list[Statement], command: CommandRunner) -> None:
    """Execute each statement in *stmts* in order."""
    for stmt in stmts:
        _exec_statement(stmt, command)


def _loop_values(loop: Eval | None) -> list[Any] | None:
    """Evaluate the loop header to a list of values (None ⇒ run once, loop=None).

    Only a plain sequence type spreads into per-iteration values; anything else
    — an int, a str, a `Problem` (a NamedTuple, so a `tuple` *subclass* that
    must not be exploded into its fields) — is a single value, looped over once.
    """
    if loop is None:
        return None
    if not isinstance(loop, (Variable, Literal)):
        raise ValueError(f'invalid loop list: {loop!r}')
    value = _eval_expr(loop.text)
    if type(value) in (list, tuple, set, frozenset, range):
        return list(value)
    return [value]


def execute(loop: Eval | None, stmts: list[Statement], *, command: CommandRunner) -> int:
    """Execute parsed statements once per loop value; return the final `rcode`."""
    try:
        values = _loop_values(loop)
    except _ExprSyntaxError as exc:
        _print_syntax_error(exc)
        variables.rcode = 1
        return 1
    except Exception as exc:
        _print_error(str(exc))
        variables.rcode = 1
        return 1
    for _ in variables.loop_through_iterable(values):
        try:
            _exec_block(stmts, command)
        except _Continue:
            continue
        except _Break:
            break
    return variables.rcode
