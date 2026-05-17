#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility functions for command-line parsing, callable inspection, history management, and file filtering. """
from __future__ import annotations

import functools
import inspect
import pathlib
import readline
import shlex
import textwrap
import typing

from solver.core.config import Config
from solver.utils.path_utils import canonical_path, iterdir_recursive

C_CMD = Config.ColorCodes.BLUE
C_LBL = Config.ColorCodes.BLACK
C_TXT = Config.ColorCodes.GRAY
_lw, _cw = 7, 29  # label column width, command column width
banner: str = f"""\
{Config.ColorCodes.CYAN}{"─" * Config.screen_width}
{Config.ColorCodes.GREEN}{Config.ColorCodes.BOLD}Project Euler Solver Shell:{Config.ColorCodes.RESET}
{Config.ColorCodes.CYAN}{"─" * Config.screen_width}
{C_LBL}{"Help":<{_lw}} {C_CMD}{"? | help":<{_cw}} {C_TXT}list all builtins, commands and aliases
{C_LBL}{" ":<{_lw}} {C_CMD}{"?<cmd> | help <cmd>":<{_cw}} {C_TXT}show help on cmd (a builtin, command or alias)
{C_LBL}{" ":<{_lw}} {C_CMD}{"<cmd> -h | --help":<{_cw}} {C_TXT}show help on cmd (a builtin or commands)
{C_LBL}{"Exit":<{_lw}} {C_CMD}{"Ctrl-D | exit":<{_cw}} {C_TXT}exit the shell
{C_LBL}{"Launch":<{_lw}} {C_CMD}{"solver [-c] [-s] [\"cmdline\"]":<{_cw}} {C_TXT}launch interactive shell
{C_LBL}{" ":<{_lw}} {C_CMD}{" ":<{_cw}} {C_TXT}-c:      stay interactive after running cmdline
{C_LBL}{" ":<{_lw}} {C_CMD}{" ":<{_cw}} {C_TXT}-s:      save session to a log-file
{C_LBL}{" ":<{_lw}} {C_CMD}{" ":<{_cw}} {C_TXT}cmdline: semicolon-separated commands to execute
{C_LBL}{"Flags":<{_lw}} {C_CMD}{"--key-word | --no-key-word":<{_cw}} {C_TXT}boolean True / False
{C_LBL}{" ":<{_lw}} {C_CMD}{"--silent":<{_cw}} {C_TXT}suppress command output{Config.ColorCodes.RESET}"""


class FuncInfo(typing.NamedTuple):
    """Cached inspection of a callable's signature and categorized parameters."""
    sig: typing.Any
    hints: dict[str, typing.Any]
    pos_params: list[typing.Any]
    var_positional: typing.Any
    kw_params: list[typing.Any]
    func: typing.Callable


def bool_flags(p_name: str, text: str) -> list[str]:
    """Return --<name> and --no-<name> flag suggestions that start with text."""
    flag, no_flag = f'--{p_name.replace("_", "-")}', f'--no-{p_name.replace("_", "-")}'
    return [f for f in (flag, no_flag) if f.startswith(text)]


def centered_msg(msg: str) -> str:
    """Print msg centered between CYAN horizontal rules."""
    left = (Config.screen_width - len(msg) - 2) // 2
    right = -(-(Config.screen_width - len(msg) - 2) // 2)
    return (f'\n{Config.ColorCodes.CYAN}{Config.ColorCodes.BOLD}{"─" * left} '
            f'{Config.ColorCodes.GREEN}{msg} '
            f'{Config.ColorCodes.CYAN}{"─" * right}{Config.ColorCodes.RESET}')


def coerce(value: str, annotation: typing.Any) -> typing.Any:
    """Coerce a raw string token to the type described by annotation."""
    if annotation is bool:
        return value.lower() in ('true', '1', 'yes')
    if annotation is int:
        try:
            return int(value.split(':')[0]) if ':' in value else int(value)
        except ValueError:
            return value
    if typing.get_origin(annotation) is typing.Literal:
        allowed = typing.get_args(annotation)
        if value not in allowed:
            raise ValueError(f'got unexpected val {value!r}, expected one of {allowed}')
    return value


def continue_on_error[**P, T](func: typing.Callable[P, T]) -> typing.Callable[P, T | None]:
    """Decorator that catches exceptions from func, prints them, and returns None instead of raising."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print('^C')
            return None
        except Exception as err:
            # noinspection PyStringConversionWithoutDunderMethod
            print(f'{func.__name__}{inspect.signature(func)}\n{getattr(func, "__doc__", ) or ""}')
            print(format_command_line(func, list(args), kwargs), f'Error: {err!s}', sep='\n')
            return None

    return wrapper


def dedup_history() -> None:
    """Remove duplicate entries from readline history, keeping the most recent occurrence of each."""
    length = readline.get_current_history_length()
    items = [readline.get_history_item(i) for i in range(1, length + 1)]
    seen: set[str] = set()
    unique: list[str] = []
    for item in reversed(items):
        if item not in seen:
            seen.add(item)
            unique.append(item)
    readline.clear_history()
    for item in reversed(unique):
        readline.add_history(item)


def format_command_line(func: str | typing.Callable, args: list[typing.Any], kwargs: dict[str, typing.Any]) -> str:
    """Format a function call as a readable string suitable for display or logging."""
    if isinstance(func, str):
        func_name: str = func
    elif isinstance(func, functools.partial):
        func_name = func.func.__name__
    elif callable(func) and not isinstance(func, type):
        func_name = func.__name__
    else:
        func_name = '<unknown>'
    args_str: str = ', '.join(map(str, args))
    kwargs_str: str = ', '.join(f"{k}={v!s}" for k, v in kwargs.items())
    return f'{func_name}({args_str}{", " if args and kwargs else ""}{kwargs_str})'


def func_info(f: typing.Callable, /, **defaults: typing.Any) -> FuncInfo:
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
    sig = inspect.signature(f)
    try:
        underlying = f.func if isinstance(f, functools.partial) else f
        hints = inspect.get_annotations(underlying, eval_str=True)
    except NameError:
        hints = {}
    to_apply: dict[str, typing.Any] = {k: v for k, v in defaults.items()
                                       if k in sig.parameters
                                       and (p := sig.parameters[k]).kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)}
    if to_apply:
        sig = sig.replace(parameters=[param for name, param in sig.parameters.items() if name not in to_apply])
        hints = {name: annotation for name, annotation in hints.items() if name not in to_apply}
        func_doc = '\n'.join(line for line in (getattr(f, '__doc__', None) or '').splitlines()
                             if not any(line.lstrip().startswith(f'{name}:') for name in to_apply))

        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
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
        return shlex.split(s)
    except ValueError:
        return s.split()


def show_value[T](value: T) -> None:
    """Print value to stdout, formatting lists, dicts, and Paths for readability."""
    if isinstance(value, list):
        print('\n'.join(map(str, value)))
    elif isinstance(value, dict):
        print('\n'.join(f'{k}: {v!s}' for k, v in value.items()))
    elif isinstance(value, pathlib.Path):
        print(canonical_path(value))
    else:
        print(str(value))


def workspace_files(text: str) -> list[str]:
    """Return filenames in the workspace directory that start with text."""
    try:
        return sorted(f for f in iterdir_recursive(Config.workspace_dir, rt='str') if f.startswith(text))
    except OSError:
        return []


def wrap_tokens(line: str, max_width: int, indent: int = 0) -> str:
    """Wrap a line of text to fit within max_width characters, breaking at colon or semicolons or word boundaries."""
    if not line or max_width <= 0 or len(line) <= max_width:
        return line
    prefix = ' ' * (indent + 1)
    lines: list[str] = [i + (':' if i[:4] == 'for ' else ';') for part in line.split(';') for i in part.split(':') if i]
    lines = [i for n, part in enumerate(lines) for i in textwrap.wrap(part,
                                                                      width=max_width,
                                                                      initial_indent='' if n == 0 else prefix,
                                                                      subsequent_indent=prefix, )]

    return '\n'.join(lines)


__all__ = (
    'C_CMD',
    'C_LBL',
    'C_TXT',
    'banner',
    'bool_flags',
    'centered_msg',
    'coerce',
    'continue_on_error',
    'dedup_history',
    'format_command_line',
    'func_info',
    'safe_split',
    'show_value',
    'workspace_files',
    'wrap_tokens',
)
