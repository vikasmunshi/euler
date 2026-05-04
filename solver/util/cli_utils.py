#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Utility functions for the interactive solver shell."""
from __future__ import annotations

from functools import partial, wraps
from inspect import get_annotations, signature
from pathlib import Path
from readline import add_history, clear_history, get_current_history_length, get_history_item
from shlex import split
from typing import Any, Callable, Literal, NamedTuple, get_args, get_origin

from solver.config import workspace_dir
from solver.util.utils import iterdir_recursive, canonical_path


class FuncInfo(NamedTuple):
    """Cached inspection of a callable's signature and categorized parameters."""
    sig: Any
    hints: dict[str, Any]
    pos_params: list[Any]
    var_positional: Any
    kw_params: list[Any]
    func: Callable


def bool_flags(p_name: str, text: str) -> list[str]:
    """Return --<name> and --no-<name> flag suggestions that start with text."""
    flag, no_flag = f'--{p_name.replace("_", "-")}', f'--no-{p_name.replace("_", "-")}'
    return [f for f in (flag, no_flag) if f.startswith(text)]


def coerce(value: str, annotation: Any) -> Any:
    """Coerce a raw string token to the type described by annotation."""
    if annotation is bool:
        return value.lower() in ('true', '1', 'yes')
    if annotation is int:
        try:
            return int(value.split(':')[0]) if ':' in value else int(value)
        except ValueError:
            return value
    if get_origin(annotation) is Literal:
        allowed = get_args(annotation)
        if value not in allowed:
            raise ValueError(f'got unexpected val {value!r}, expected one of {allowed}')
    return value


def continue_on_error[**P, T](func: Callable[P, T]) -> Callable[P, T | None]:
    """Decorator that catches exceptions from func, prints them, and returns None instead of raising."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print('^C')
            return None
        except Exception as err:
            print(f'{func.__name__}{signature(func)}\n{getattr(func, "__doc__", ) or ""}')
            print(format_command_line(func, list(args), kwargs), f'Error: {err!s}', sep='\n')
            return None

    return wrapper


def dedup_history() -> None:
    """Remove duplicate entries from readline history, keeping the most recent occurrence of each."""
    length = get_current_history_length()
    items = [get_history_item(i) for i in range(1, length + 1)]
    seen: set[str] = set()
    unique: list[str] = []
    for item in reversed(items):
        if item not in seen:
            seen.add(item)
            unique.append(item)
    clear_history()
    for item in reversed(unique):
        add_history(item)


def format_command_line(func: str | Callable, args: list[Any], kwargs: dict[str, Any]) -> str:
    """Format a function call as a readable string suitable for display or logging."""
    if isinstance(func, str):
        func_name: str = func
    elif isinstance(func, partial):
        func_name = func.func.__name__
    elif callable(func) and not isinstance(func, type):
        func_name = func.__name__
    else:
        func_name = '<unknown>'
    args_str: str = ', '.join(map(str, args))
    kwargs_str: str = ', '.join(f"{k}={v!s}" for k, v in kwargs.items())
    return f'{func_name}({args_str}{", " if args and kwargs else ""}{kwargs_str})'


def func_info(f: Callable, /, **defaults: Any) -> FuncInfo:
    """
    Return signature metadata for *func*, pre-binding any *defaults*.

    Parameters named in *defaults* that are POSITIONAL_OR_KEYWORD or KEYWORD_ONLY
    are injected at call time and stripped from the returned signature, annotations, and
    docstring — as if they were never declared.

    Args:
        f: The callable to inspect.
        **defaults: Pre-bound values keyed by parameter name.

    Returns:
        FuncInfo with sig, hints, pos_params, var_positional, kw_params, and func
        reflecting only the parameters visible to the caller.
    """
    sig = signature(f)
    try:
        underlying = f.func if isinstance(f, partial) else f
        hints = get_annotations(underlying, eval_str=True)
    except NameError:
        hints = {}
    to_apply: dict[str, Any] = {k: v for k, v in defaults.items()
                                if k in sig.parameters
                                and (p := sig.parameters[k]).kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)}
    if to_apply:
        sig = sig.replace(parameters=[param for name, param in sig.parameters.items() if name not in to_apply])
        hints = {name: annotation for name, annotation in hints.items() if name not in to_apply}
        func_doc = '\n'.join(line for line in (getattr(f, '__doc__', None) or '').splitlines()
                             if not any(line.lstrip().startswith(f'{name}:') for name in to_apply))

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            kwargs.update(to_apply)
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        wrapper.__doc__ = func_doc
        wrapper.__annotations__ = hints
        func = wrapper
    else:
        func = f

    params = list(sig.parameters.values())
    return FuncInfo(
        sig=sig,
        hints=hints,
        pos_params=[p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)],
        var_positional=next((p for p in params if p.kind == p.VAR_POSITIONAL), None),
        kw_params=[p for p in params if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)],
        func=func,
    )


def safe_split(s: str) -> list[str]:
    """Split a shell-style string, falling back to str.split on parse errors."""
    try:
        return split(s)
    except ValueError:
        return s.split()


def show_value[T](value: T) -> None:
    """Print value to stdout, formatting lists, dicts, and Paths for readability."""
    if isinstance(value, list):
        print('\n'.join(map(str, value)))
    elif isinstance(value, dict):
        print('\n'.join(f'{k}: {v!s}' for k, v in value.items()))
    elif isinstance(value, Path):
        print(canonical_path(value))
    else:
        print(str(value))


def workspace_files(text: str) -> list[str]:
    """Return filenames in the workspace directory that start with text."""
    try:
        return sorted(f for f in iterdir_recursive(workspace_dir, rt='str') if f.startswith(text))
    except OSError:
        return []


__all__ = (
    'bool_flags',
    'coerce',
    'continue_on_error',
    'dedup_history',
    'format_command_line',
    'func_info',
    'safe_split',
    'show_value',
    'workspace_files',
)
