#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Module for registering functions as shell commands with type-safe argument
coercion and completion support.

This module allows functions to be registered as shell commands without
modifying their behavior. It provides argument type validation and supports
automatic completion of command arguments. The registered functions can
still be used as standard Python functions.

Functions:
- _coerce: Performs type coercion of input values based on their annotated
  types. Handles common Python annotations including Literal, Optional,
  bool, int, float, and str.
- register: A decorator for registering functions as shell commands, providing
  automatic type coercion, argument parsing, and completion support.
"""
from __future__ import annotations

import ast
import enum
import inspect
import os
import random
import types
import typing
from typing import Any, Callable, Iterable

from prompt_toolkit.completion import Completion
from rich.text import Text

from solver.config import config
from solver.core.problems import problems
from solver.shell.shell import Context, command


# ---------------------------------------------------------------------------
# register - decorator for external functions
# ---------------------------------------------------------------------------

def _coerce(value: Any, annotation: Any) -> Any:
    """Best-effort coercion of a token string to the parameter's annotated type.

    Strategy:
    * If *value* is not a string, pass it through unchanged.
    * `inspect.Parameter.empty` / `Any` → leave as string.
    * `Literal[...]` → validate membership and return the matched member
      (typed, so `Literal[1, 2]` + `'1'` → `1`); raises `ValueError` on mismatch.
    * `X | None` / `Optional[X]` / `Union[X, None]` →
      'none'/'null'/'' (case-insensitive) become 'None';
      otherwise coerce to the first non-'None' argument.
    * `bool` → truthy strings '1/true/yes/y/on' (case-insensitive) → 'True';
      everything else → 'False'.
    * `int`, `float`, `str` → call the constructor directly.
    * Anything else → :func:`ast.literal_eval` (so '[1,2]', '(1,2)',
      '{'a':1}' work); on failure, the 'ValueError'/'SyntaxError'
      propagates to the adapter's top-level except block.
    """
    if not isinstance(value, str) or annotation is inspect.Parameter.empty or annotation is Any:
        return value
    # Handle Optional / Union with None (both `Optional[X]` / `Union[X, None]` and PEP 604 `X | None`).
    origin = typing.get_origin(annotation)
    # `Literal[...]` — validate membership and coerce to the member's type.
    if origin is typing.Literal:
        for member in typing.get_args(annotation):
            try:
                if type(member) is bool:
                    if _coerce(value, bool) == member:
                        return member
                elif type(member) is str:
                    if value == member:
                        return member
                else:
                    if type(member)(value) == member:
                        return member
            except (ValueError, TypeError):
                continue
        allowed: list[str] = [repr(m) for m in typing.get_args(annotation)]
        if len(allowed) >= 10:
            allowed_str: str = f'{allowed[0]}...{allowed[-1]}'
        else:
            allowed_str = ', '.join(allowed)
        raise ValueError(f'{value!r} is not one of {allowed_str}')
    if origin is typing.Union or origin is types.UnionType:
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        if value.strip().lower() in ('none', 'null', ''):
            return None
        return _coerce(value, args[0]) if args else value
    if annotation is bool:
        return value.strip().lower() in ('1', 'true', 'yes', 'y', 'on')
    if annotation in (int, float, str):
        return annotation(value)
    if isinstance(annotation, type) and issubclass(annotation, enum.Enum):
        return annotation(value)
    return ast.literal_eval(value)


def register[**P, T](
        name: str | None = None,
        *,
        help: str = '',
        usage: str = '',
        aliases: tuple[str, ...] = (),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator that registers *func* as a shell command **without modifying it**.

    Unlike :func:`command` (which requires a '(ctx, *args)' signature), :func:`register`
    introspects the wrapped function's signature and builds an adapter that:

    * splits positional tokens from 'key=value' tokens,
    * coerces values to the parameter's annotated type
      ('bool', 'int', 'float', 'str', 'Optional[...]' are handled;
      anything else is forwarded verbatim as a string).  Values forwarded via
      '**kwargs' are coerced against the '**kwargs' annotation when present,
    * invokes the wrapped function unchanged,
    * prints a non-'None' return value via the shared console.

    Keyword-only parameters must be supplied as 'name=value' tokens (there is no
    positional form for them, matching Python's call semantics).

    The wrapped function is returned unchanged, so it remains usable as a plain
    Python callable from any module.

    Example
    -------
    >>> @register(name='echo', help='Echo arguments.', usage='echo <message> [times=N]', aliases=('e',))
    ... def echo(message: str, times: int = 1) -> str:
    ...     return ' '.join([message] * times)
    """

    def _register(func: Callable[P, T]) -> Callable[P, T]:
        signature: inspect.Signature = inspect.signature(func, eval_str=True)
        params = list(signature.parameters.values())
        param_by_name: dict[str, inspect.Parameter] = {p.name: p for p in params}
        positional_params: list[inspect.Parameter] = [
            p for p in params
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                          inspect.Parameter.POSITIONAL_OR_KEYWORD,
                          inspect.Parameter.VAR_POSITIONAL)
        ]
        var_keyword_param: inspect.Parameter | None = next(
            (p for p in params if p.kind == inspect.Parameter.VAR_KEYWORD),
            None,
        )

        def _resolve_problem_number_token(tok: str) -> str:
            """Map 'next'/'random' aliases to a concrete problem-number string.

            * 'next'   → first problem in `problems.problems_list` not in
              `problems.solved_problems`, falling back to the last problem.
            * 'random' → a random choice from the unsolved problems, falling
              back to the full list when everything is solved.
            * anything else → returned unchanged so normal int coercion runs.
            """
            if tok == 'next':
                nxt = next(
                    (p for p in problems.problems_list if p not in problems.solved_problems),
                    problems.problems_list[-1],
                )
                return str(nxt.number)
            if tok == 'random':
                unsolved = [p for p in problems.problems_list if p not in problems.solved_problems]
                pool = unsolved or problems.problems_list
                return str(random.choice(pool).number)
            return tok

        def _coerce_positional(index: int, tok: str) -> Any:
            """Coerce the *index*-th positional token against `positional_params`.

            Falls back to the trailing `*args` parameter's annotation when the
            index exceeds the fixed positionals; otherwise leaves *tok* as-is.
            """
            if index < len(positional_params) and positional_params[index].kind != inspect.Parameter.VAR_POSITIONAL:
                param = positional_params[index]
                if param.name == 'problem_number':
                    tok = _resolve_problem_number_token(tok)
                return _coerce(tok, param.annotation)
            if positional_params and positional_params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
                return _coerce(tok, positional_params[-1].annotation)
            return tok

        def _coerce_keyword(key: str, value: str) -> Any:
            """Coerce a `key=value` token against the named parameter's annotation,
            falling back to the `**kwargs` annotation when *key* is not a declared
            *keyword-bindable* parameter (i.e. positional-only and var-keyword
            names don't shadow the `**kwargs` fallback)."""
            if key == 'problem_number':
                value = _resolve_problem_number_token(value)
            declared = param_by_name.get(key)
            if declared is not None and declared.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
            ):
                ann = declared.annotation
            elif var_keyword_param is not None:
                ann = var_keyword_param.annotation
            else:
                ann = inspect.Parameter.empty
            return _coerce(value, ann)

        def _parse(args: tuple[str, ...]) -> tuple[list[Any], dict[str, Any]]:
            pos_tokens: list[str] = []
            kw_tokens: dict[str, str] = {}
            for tok in args:
                if '=' in tok and not tok.startswith('='):
                    k, _, v = tok.partition('=')
                    kw_tokens[k] = v
                else:
                    pos_tokens.append(tok)
            coerced_pos: list[Any] = [_coerce_positional(i, tok) for i, tok in enumerate(pos_tokens)]
            coerced_kw: dict[str, Any] = {k: _coerce_keyword(k, v) for k, v in kw_tokens.items()}
            return coerced_pos, coerced_kw

        def _completer(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
            """Suggest completions for a `register()`-wrapped command.

            * If *incomplete* contains '=', complete the value side using
              annotation-aware hints ('true'/'false' for `bool`,
              'none' for `Optional[...]`, literal members for `Literal[...]`).
              Special case: 'solution=' lists executables in the workspace dir.
            * Otherwise, suggest `Literal` members for the current positional
              slot (including `VAR_POSITIONAL`), then 'name=' for every
              keyword-bindable parameter not yet supplied on the current line.
              Special case: 'problem_number' yields rich `Completion` objects
              with the problem title as display text.
            """
            # Value-side completion: 'key=<partial>'.
            if '=' in incomplete and not incomplete.startswith('='):
                key, _, partial = incomplete.partition('=')
                # Special case: list executable files in the workspace dir.
                if key == 'solution':
                    try:
                        return [
                            f'solution={f.name}'
                            for f in sorted(config.workspace_dir.iterdir())
                            if f.is_file() and os.access(f, os.X_OK) and f.name.startswith(partial)
                        ]
                    except OSError:
                        return []
                declared = param_by_name.get(key)
                if declared is not None and declared.kind in (
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.KEYWORD_ONLY,
                ):
                    ann = declared.annotation
                elif var_keyword_param is not None:
                    ann = var_keyword_param.annotation
                else:
                    ann = inspect.Parameter.empty
                hints: list[str] = []
                origin = typing.get_origin(ann)
                if origin is typing.Union or origin is types.UnionType:
                    hints.append('none')
                    inner = [a for a in typing.get_args(ann) if a is not type(None)]
                    if inner and inner[0] is bool:
                        hints.extend(('true', 'false'))
                    elif inner and typing.get_origin(inner[0]) is typing.Literal:
                        hints.extend(str(v) for v in typing.get_args(inner[0]))
                    elif inner and isinstance(inner[0], type) and issubclass(inner[0], enum.Enum):
                        hints.extend(str(v.value) for v in inner[0])
                elif ann is bool:
                    hints.extend(('true', 'false'))
                elif origin is typing.Literal:
                    hints.extend(str(v) for v in typing.get_args(ann))
                elif isinstance(ann, type) and issubclass(ann, enum.Enum):
                    hints.extend(str(v.value) for v in ann)
                return [f'{key}={h}' for h in hints if h.startswith(partial)]
            # Name-side and positional completion.
            supplied: set[str] = set()
            for tok in ctx.argv:
                if '=' in tok and not tok.startswith('='):
                    supplied.add(tok.partition('=')[0])
            candidates: list[str | Completion] = []
            # Positional hints: determine which slot we're filling.
            pos_count = sum(
                1 for t in ctx.argv
                if not ('=' in t and not t.startswith('='))
            )
            if incomplete:
                pos_count -= 1  # incomplete token is already in ctx.argv; don't count it
            pos_param: inspect.Parameter | None = None
            if pos_count < len(positional_params) and \
                    positional_params[pos_count].kind != inspect.Parameter.VAR_POSITIONAL:
                pos_param = positional_params[pos_count]
            elif positional_params and positional_params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
                pos_param = positional_params[-1]
            if pos_param is not None:
                # Special case: 'problem_number' — emit 'next'/'random' aliases
                # first, then each known problem number with its title as
                # display text.
                if pos_param.name == 'problem_number':
                    for alias, display in (
                            ('next', 'next unsolved problem'),
                            ('random', 'random unsolved problem'),
                    ):
                        if alias.startswith(incomplete):
                            candidates.append(
                                Completion(alias, start_position=-len(incomplete), display=display)
                            )
                    for problem in problems.problems_list:
                        s = str(problem.number)
                        if s.startswith(incomplete):
                            candidates.append(Completion(s, start_position=-len(incomplete), display=str(problem)))
                elif typing.get_origin(pos_param.annotation) is typing.Literal:
                    candidates.extend(
                        str(v)
                        for v in typing.get_args(pos_param.annotation)
                        if str(v).startswith(incomplete)
                    )
            # Keyword name hints.
            for p in params:
                if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                  inspect.Parameter.KEYWORD_ONLY):
                    continue
                if p.name in supplied:
                    continue
                if p.name.startswith(incomplete):
                    candidates.append(f'{p.name}=')
            return candidates

        @command(name=name, help=help, usage=usage, aliases=aliases, completer=_completer)
        def _adapter(ctx: Context, *args: str) -> None:
            try:
                pos_args, kw_args = _parse(args)
            except (ValueError, SyntaxError) as exc:
                ctx.console.print(f'[error]argument error:[/error] {exc}')
                if usage:
                    _usage_line = Text('usage: ', style='muted')
                    _usage_line.append(usage, style='accent')
                    ctx.console.print(_usage_line)
                return
            call_parts = [repr(a) for a in pos_args]
            call_parts.extend(f'{k}={v!r}' for k, v in kw_args.items())
            call_str = f'{name}({", ".join(call_parts)})'
            try:
                result = func(*pos_args, **kw_args)
            except KeyboardInterrupt:
                raise
            except Exception:  # noqa: BLE001 — top-level UX boundary
                ctx.console.print(f'[muted]{call_str}[/muted] [accent]→[/accent] error')
                ctx.console.print_exception()
                return
            result_str: str = 'ok' if result is None else str(result)
            ctx.console.print(f'[muted]{call_str}[/muted] [accent]→[/accent] {result_str}')

        # Preserve metadata for downstream tools / repr / debugging.
        _adapter.__wrapped__ = func  # type: ignore[attr-defined]
        return func

    return _register


# ---------------------------------------------------------------------------
# module exports
# ---------------------------------------------------------------------------
__all__ = ('register',)
