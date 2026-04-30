#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Utility functions for the interactive solver shell."""
from __future__ import annotations

from functools import partial
from inspect import get_annotations, signature
from readline import add_history, clear_history, get_current_history_length, get_history_item
from shlex import split
from typing import Any, Callable, Literal, NamedTuple, get_args, get_origin

__all__ = ['FuncInfo', 'bool_flags', 'coerce', 'dedup_history', 'func_info', 'safe_split']


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
        func_doc = '\n'.join(line for line in (f.__doc__ or '').splitlines()
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
