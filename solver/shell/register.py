#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `@register` decorator: register a function as a shell command with type-safe coercion and completion.

Functions are registered as shell commands without modifying their behavior, with type-safe argument
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

__all__ = ['register']

import ast
import enum
import inspect
import os
import types
import typing
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Iterable

from prompt_toolkit.completion import Completion
from rich.text import Text

from solver.config import ExitCodes, config
from solver.core.problems import problems
from solver.shell.command import Context, command


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


def _usage_from_signature(cmd_name: str, params: list[inspect.Parameter], quietable: bool) -> str:
    """Synthesize a usage string from the command name and its (ctx-dropped) params.

    Required parameters appear on the first line as `<name>`; optional ones (and the
    synthetic `--silent` for a quietable command) follow one per line as `[name=hint]`,
    with bools rendered as their activating flag.
    """

    def _hint(ann: Any) -> str:
        origin = typing.get_origin(ann)
        if origin is typing.Literal:
            return '|'.join(str(v) for v in typing.get_args(ann))
        if origin is typing.Union or origin is types.UnionType:
            inner = [a for a in typing.get_args(ann) if a is not type(None)]
            return f'{_hint(inner[0]) if inner else "<value>"}|none'
        if isinstance(ann, type) and issubclass(ann, enum.Enum):
            return '|'.join(str(v.value) for v in ann)
        if ann in (int, float, str):
            return f'<{ann.__name__}>'
        return '<value>'

    def _default(value: Any) -> str:
        if isinstance(value, enum.Enum):
            return str(value.value)
        return "''" if value == '' else str(value)

    required: list[str] = []
    optional: list[str] = []
    for p in params:
        nm = p.name
        if p.kind is inspect.Parameter.VAR_POSITIONAL:
            if typing.get_origin(p.annotation) is typing.Literal:
                optional.append(f'[{_hint(p.annotation)} ...]')
            else:
                optional.append(f'[<{nm}>...]')
        elif p.kind is inspect.Parameter.VAR_KEYWORD:
            optional.append('[key=value ...]')
        elif p.annotation is bool:
            flag = nm.replace('_', '-')
            if p.default is inspect.Parameter.empty:
                required.append(f'<{nm}=true|false>')
            elif p.default is True:
                optional.append(f'[{nm}=false|--no-{flag}]')
            else:
                optional.append(f'[{nm}=true|--{flag}]')
        elif p.default is inspect.Parameter.empty:
            hint = _hint(p.annotation)
            if p.kind is inspect.Parameter.KEYWORD_ONLY:
                required.append(f'<{nm}={hint}>')
            elif typing.get_origin(p.annotation) is typing.Literal:
                required.append(f'<{hint}>')
            else:
                required.append(f'<{nm}>')
        else:
            optional.append(f'[{nm}={_hint(p.annotation)}] (default {_default(p.default)})')
    if quietable:
        optional.append('[silent=true|--silent]')
    head = f'\t{cmd_name}' + (f' {" ".join(required)}' if required else '')
    return '\n'.join([head, *(f'\t{opt}' for opt in optional)])


@dataclass
class _CommandSpec:
    """The introspected, token-driven view of a `register()`-wrapped function.

    Built once per registration by :func:`_build_command_spec`, then threaded
    through the parsing, coercion, completion, and dispatch helpers so each can
    stay a plain module function instead of a closure over `register`'s locals.
    """

    func: Callable[..., int]
    name: str | None
    cmd_name: str
    help_text: str
    usage: str
    pass_ctx: bool
    quietable: bool
    params: list[inspect.Parameter]
    param_by_name: dict[str, inspect.Parameter]
    positional_params: list[inspect.Parameter]
    var_keyword_param: inspect.Parameter | None
    bool_flags: dict[str, tuple[str, bool]]


def _build_bool_flags(params: list[inspect.Parameter], quietable: bool) -> dict[str, tuple[str, bool]]:
    """Build the CLI-style boolean flag table: '--flag' / '--no-flag'.

    For each keyword-bindable parameter with a strict `bool` annotation, generate
    flag literals (without the leading '--') mapped to (param_name, value).
    Underscores in the parameter name become dashes.
    * no default → both '--flag' (True) and '--no-flag' (False)
    * default False → '--flag' (True)
    * default True  → '--no-flag' (False)

    A quietable command additionally gains a synthetic `--silent` flag: it is not
    a function parameter (the adapter pops it and runs the body with the shared
    console quiet), but riding `bool_flags` gives it parsing and completion for free.
    """
    bool_flags: dict[str, tuple[str, bool]] = {}
    for p in params:
        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                          inspect.Parameter.KEYWORD_ONLY):
            continue
        if p.annotation is not bool:
            continue
        flag_base = p.name.replace('_', '-')
        entries: list[tuple[str, bool]] = []
        if p.default is inspect.Parameter.empty:
            entries.append((flag_base, True))
            entries.append((f'no-{flag_base}', False))
        elif p.default is False:
            entries.append((flag_base, True))
        elif p.default is True:
            entries.append((f'no-{flag_base}', False))
        for flag_lit, flag_val in entries:
            if flag_lit in bool_flags:
                raise ValueError(
                    f'boolean flag --{flag_lit} collides between parameters '
                    f'{bool_flags[flag_lit][0]!r} and {p.name!r}'
                )
            bool_flags[flag_lit] = (p.name, flag_val)
    if quietable:
        bool_flags['silent'] = ('silent', True)
    return bool_flags


def _build_command_spec(
        func: Callable[..., int],
        name: str | None,
        help_text: str,
        pass_ctx: bool,
        quietable: bool,
) -> _CommandSpec:
    """Introspect *func* and pre-compute everything the token-driven helpers need."""
    if getattr(func, '__check_workspace_lock__', False):
        help_text += ' [warning]§[/warning]'
    if getattr(func, '__refresh_workspace_vars__', False):
        help_text += ' [warning]↻[/warning]'
    if quietable:
        help_text += ' [warning]»[/warning]'
    cmd_name: str = name or func.__name__.lstrip('_').replace('_', '-')
    signature: inspect.Signature = inspect.signature(func, eval_str=True)
    params = list(signature.parameters.values())
    if pass_ctx:
        # The leading parameter receives the live Context, injected by the
        # adapter — it is not parsed from user tokens, so drop it from every
        # token-driven computation below (coercion, flags, completion).
        if not params or params[0].kind not in (inspect.Parameter.POSITIONAL_ONLY,
                                                inspect.Parameter.POSITIONAL_OR_KEYWORD):
            raise ValueError(f'{getattr(func, "__name__", "?")}: '
                             'pass_ctx=True requires a leading positional context parameter')
        params = params[1:]
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
    return _CommandSpec(
        func=func,
        name=name,
        cmd_name=cmd_name,
        help_text=help_text,
        usage=_usage_from_signature(cmd_name, params, quietable),
        pass_ctx=pass_ctx,
        quietable=quietable,
        params=params,
        param_by_name={p.name: p for p in params},
        positional_params=positional_params,
        var_keyword_param=var_keyword_param,
        bool_flags=_build_bool_flags(params, quietable),
    )


def _keyword_annotation(spec: _CommandSpec, key: str) -> Any:
    """Resolve the annotation that governs a `key=value` token.

    Uses the named parameter's annotation when *key* is a declared
    *keyword-bindable* parameter, otherwise falls back to the `**kwargs`
    annotation (so positional-only and var-keyword names don't shadow it), and
    finally `inspect.Parameter.empty` when neither applies.
    """
    declared = spec.param_by_name.get(key)
    if declared is not None and declared.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
    ):
        return declared.annotation
    if spec.var_keyword_param is not None:
        return spec.var_keyword_param.annotation
    return inspect.Parameter.empty


def _coerce_positional(spec: _CommandSpec, index: int, tok: str) -> Any:
    """Coerce the *index*-th positional token against `spec.positional_params`.

    Falls back to the trailing `*args` parameter's annotation when the index
    exceeds the fixed positionals; otherwise leaves *tok* as-is.
    """
    positional_params = spec.positional_params
    if index < len(positional_params) and positional_params[index].kind != inspect.Parameter.VAR_POSITIONAL:
        return _coerce(tok, positional_params[index].annotation)
    if positional_params and positional_params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
        return _coerce(tok, positional_params[-1].annotation)
    return tok


def _coerce_keyword(spec: _CommandSpec, key: str, value: str) -> Any:
    """Coerce a `key=value` token against the named parameter's annotation."""
    if spec.quietable and key == 'silent':
        return _coerce(value, bool)
    return _coerce(value, _keyword_annotation(spec, key))


class _ArgError(ValueError):
    """An argument parse/coercion failure, tagged with the offending token's index
    in the command's argument list so the adapter can point a caret at it."""

    def __init__(self, message: str, index: int) -> None:
        super().__init__(message)
        self.index = index


def _parse_args(spec: _CommandSpec, args: tuple[str, ...]) -> tuple[list[Any], dict[str, Any]]:
    """Split user tokens into coerced positional / keyword arguments.

    Parse/coercion failures raise `_ArgError` carrying the offending token's index
    into *args*, so the caller can underline it in the echoed command line.
    """
    pos: list[tuple[int, str]] = []  # (args index, token)
    kw: list[tuple[int, str, str]] = []  # (args index, key, value)
    flag_kw: dict[str, tuple[int, bool]] = {}
    for idx, tok in enumerate(args):
        if tok.startswith('--') and len(tok) > 2 and '=' not in tok:
            flag = tok[2:]
            if flag not in spec.bool_flags:
                raise _ArgError(f'unknown flag: {tok}', idx)
            param_name, flag_value = spec.bool_flags[flag]
            if param_name in flag_kw:
                raise _ArgError(f'conflicting boolean flag for {param_name!r}: {tok}', idx)
            flag_kw[param_name] = (idx, flag_value)
        elif '=' in tok and not tok.startswith('='):
            k, _, v = tok.partition('=')
            kw.append((idx, k, v))
        else:
            pos.append((idx, tok))
    coerced_pos: list[Any] = []
    for slot, (idx, tok) in enumerate(pos):
        try:
            coerced_pos.append(_coerce_positional(spec, slot, tok))
        except (ValueError, SyntaxError) as exc:
            raise _ArgError(str(exc), idx) from exc
    coerced_kw: dict[str, Any] = {}
    for idx, key, value in kw:
        try:
            coerced_kw[key] = _coerce_keyword(spec, key, value)
        except (ValueError, SyntaxError) as exc:
            raise _ArgError(str(exc), idx) from exc
    for flag_name, (idx, flag_bool) in flag_kw.items():
        if flag_name in coerced_kw:
            raise _ArgError(f'boolean flag for {flag_name!r} conflicts with {flag_name}=... argument', idx)
        coerced_kw[flag_name] = flag_bool
    return coerced_pos, coerced_kw


def _print_arg_error(spec: _CommandSpec, ctx: Context, args: tuple[str, ...], exc: Exception) -> None:
    """Report an argument error with the offending token under a caret, then usage —
    consistent with the lexer/interpreter syntax-error display."""
    ctx.console.print(f'[error]argument error:[/error] {exc}')
    index = getattr(exc, 'index', None)
    if isinstance(index, int) and 0 <= index < len(args):
        line = ' '.join([spec.cmd_name, *args])
        offset = len(spec.cmd_name) + 1 + sum(len(args[j]) + 1 for j in range(index))
        located = Text(f'  {line}\n', style='muted')
        located.append('  ' + ' ' * offset + '^', style='warning')
        located.append(f'  (col {offset + 1})', style='muted')
        ctx.console.print(located)
    if spec.usage:
        usage_line = Text('usage: ', style='muted')
        usage_line.append(spec.usage, style='accent')
        ctx.console.print(usage_line)


def _complete(spec: _CommandSpec, ctx: Context, incomplete: str) -> Iterable[str | Completion]:
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
        ann = _keyword_annotation(spec, key)
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
        if tok.startswith('--') and len(tok) > 2 and '=' not in tok:
            flag = tok[2:]
            if flag in spec.bool_flags:
                supplied.add(spec.bool_flags[flag][0])
        elif '=' in tok and not tok.startswith('='):
            supplied.add(tok.partition('=')[0])
    # Flag-style completion when the user starts typing '-' / '--'.
    if incomplete.startswith('-'):
        return [
            f'--{flag}'
            for flag, (param_name, _) in spec.bool_flags.items()
            if param_name not in supplied and f'--{flag}'.startswith(incomplete)
        ]
    candidates: list[str | Completion] = []
    # Positional hints: determine which slot we're filling.
    pos_count = sum(
        1 for t in ctx.argv
        if not ('=' in t and not t.startswith('='))
        and not (t.startswith('--') and len(t) > 2 and '=' not in t)
    )
    if incomplete:
        pos_count -= 1  # incomplete token is already in ctx.argv; don't count it
    positional_params = spec.positional_params
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
                    ('{next}', 'next unsolved problem'),
                    ('{random}', 'random unsolved problem'),
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
    for p in spec.params:
        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                          inspect.Parameter.KEYWORD_ONLY):
            continue
        if p.name in supplied:
            continue
        if p.name.startswith(incomplete):
            candidates.append(f'{p.name}=')
    return candidates


def _run_command(spec: _CommandSpec, ctx: Context, args: tuple[str, ...]) -> int:
    """Parse *args*, invoke the wrapped function, and map outcomes to exit codes."""
    try:
        pos_args, kw_args = _parse_args(spec, args)
    except (ValueError, SyntaxError) as exc:
        _print_arg_error(spec, ctx, args, exc)
        return ExitCodes.EXIT_USAGE
    # `silent` is the adapter's flag, not the function's: pop it and run the
    # body with the shared console quiet (restored before any output, so the
    # `cmd() → rc` summary and any errors still show).
    silent = bool(kw_args.pop('silent', False)) if spec.quietable else False
    call_parts = [repr(a) for a in pos_args]
    call_parts.extend(f'{k}={v!r}' for k, v in kw_args.items())
    call_str = f'{spec.name}({", ".join(call_parts)})'
    if spec.pass_ctx:
        pos_args = [ctx] + pos_args
    prev_quiet, ctx.console.quiet = ctx.console.quiet, ctx.console.quiet or silent
    try:
        try:
            result = spec.func(*pos_args, **kw_args)
        finally:
            ctx.console.quiet = prev_quiet
    except KeyboardInterrupt:
        ctx.console.print(f'[muted]{call_str}[/muted] [accent.dim]→[/accent.dim] interrupted')
        return ExitCodes.EXIT_ERROR
    except TypeError as exc:
        # An arg-binding error (wrong count / unexpected keyword). Relabel the
        # internal function name as the command name, then report it like any
        # other argument error (message + usage; no caret — the token is missing).
        message = str(exc).replace(f'{spec.func.__name__}(', f'{spec.cmd_name}(', 1)
        _print_arg_error(spec, ctx, args, TypeError(message))
        return ExitCodes.EXIT_USAGE
    except Exception:  # noqa: BLE001 — top-level UX boundary
        ctx.console.print(f'[muted]{call_str}[/muted] [accent.dim]→[/accent.dim] error')
        ctx.console.print_exception()
        return ExitCodes.EXIT_ERROR
    # The command's success summary (`cmd(...) → rc`) is emitted by the
    # interpreter's result echo, not here. The command owns its contract:
    # its `int` return *is* the exit code, passed through verbatim.
    return result


def register[**P](
        *,
        help_text: str = '',
        aliases: tuple[str, ...] = (),
        pass_ctx: bool = False,
        quietable: bool = False,
) -> Callable[[Callable[P, int]], Callable[P, int]]:
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

    When 'pass_ctx=True', the wrapped function must declare a leading positional
    parameter (conventionally 'ctx: Context'); the adapter injects the live
    :class:`Context` there and parses user tokens against the *remaining*
    parameters.  This lets a 'register()' command reach shell state (e.g.
    'ctx.shell') while keeping the decorator's argument coercion and completion.

    Keyword-only parameters must be supplied as 'name=value' tokens (there is no
    positional form for them, matching Python's call semantics).

    Boolean parameters can additionally be set with CLI-style flags.  Underscores
    in the parameter name become dashes (e.g. 'dry_run' → '--dry-run').

    * no default (required) → both '--name' (True) and '--no-name' (False).
    * default 'False'       → '--name' (True).
    * default 'True'        → '--no-name' (False).

    Flags and 'name=value' are mutually exclusive for the same parameter; an
    unknown flag or a conflicting combination raises a 'ValueError' that the
    adapter reports through the shared console.

    The wrapped function is returned unchanged, so it remains usable as a plain
    Python callable from any module.

    Example
    -------
    >>> @register(name='echo', help_text='Echo arguments.', usage='echo <message> [times=N]', aliases=('e',))
    ... def echo(message: str, times: int = 1) -> str:
    ...     return ' '.join([message] * times)
    """

    def _register(func: Callable[P, int]) -> Callable[P, int]:
        name = func.__name__.replace('_', '-')
        spec = _build_command_spec(func, name, help_text, pass_ctx, quietable)

        def _completer(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
            return _complete(spec, ctx, incomplete)

        @command(name=name, help_text=spec.help_text, usage=spec.usage, aliases=aliases, completer=_completer)
        @wraps(func)
        def _adapter(ctx: Context, *args: str) -> int:
            return _run_command(spec, ctx, args)

        # Preserve metadata for downstream tools / repr / debugging.
        _adapter.__wrapped__ = func  # type: ignore[attr-defined]
        return func

    return _register
