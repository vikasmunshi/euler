#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Shared utilities: directory helpers, git integration, and shell command wrappers."""
from __future__ import annotations

from functools import lru_cache, partial, wraps
from inspect import signature
from os import getenv
from pathlib import Path
from subprocess import run
from typing import Any, Callable, Generator, Literal, overload

from solver.config import keys_file, root_dir, upload_keys_to_origin

__all__ = [
    'continue_on_error',
    'disabled',
    'format_command_line',
    'get_gh_user_email',
    'get_gh_user_email',
    'get_repo_owner_email',
    'is_admin',
    'is_unchanged',
    'iterdir_recursive',
    'run_command',
    'run_script',
    'show_value',
    'upload_keys',
    'write_file',
]


@lru_cache(maxsize=None)
def get_repo_owner_email() -> str:
    """Return the GitHub repository owner's email, cached after the first lookup."""
    repo_owner: str | None = run_command('gh repo view --json owner --jq .owner.login')
    if not repo_owner:
        raise ValueError('Error: could not get repository owner')
    owner_email: str | None = run_command(f'gh api users/{repo_owner} --jq .email')
    if not owner_email:
        raise ValueError('Error: could not get owner email')
    return owner_email


@lru_cache(maxsize=None)
def get_gh_user_email() -> str:
    """Return the authenticated GitHub user's email, cached after the first lookup."""
    is_authenticated: str | None = run_command('gh auth status')
    if not is_authenticated:
        raise ValueError('Error: gh CLI is not authenticated')
    gh_username: str | None = run_command('gh api user --jq .login')
    if not gh_username:
        raise ValueError('Error: could not get GitHub authenticated username')
    gh_user_email: str | None = run_command('gh api user --jq .email')
    if not gh_user_email:
        raise ValueError("Error: could not get GitHub authenticated user's email")
    return gh_user_email


@lru_cache(maxsize=None)
def is_admin() -> bool:
    """Return True if the authenticated GitHub user is the repository owner."""
    return get_gh_user_email() == get_repo_owner_email()


def is_unchanged(file: Path) -> bool:
    """Return True if the file has no diff against origin/master."""
    changes = run_command(f'git --no-pager diff origin/master -- {file.relative_to(root_dir).as_posix()}')
    return changes is not None and changes.strip().strip('\n') == ''


@overload
def iterdir_recursive(directory: Path, *,
                      rt: Literal['path'] = ...,
                      _root: Path | None = ...) -> Generator[Path, None, None]:
    ...


@overload
def iterdir_recursive(directory: Path, *,
                      rt: Literal['str'],
                      _root: Path | None = ...) -> Generator[str, None, None]:
    ...


def iterdir_recursive(directory: Path, *,
                      rt: Literal['path', 'str'] = 'path',
                      _root: Path | None = None, ) -> Generator[Path | str, None, None]:
    """Yield all files under the directory, returning Paths or POSIX strings relative to directory per rt."""
    if not directory.exists():
        return
    if directory.is_file():
        return
    root = _root or directory
    for item in directory.iterdir():
        if item.is_dir():
            yield from iterdir_recursive(item, rt=rt, _root=root)
        elif item.is_file():
            if rt == 'str':
                yield item.relative_to(root).as_posix()
            else:
                yield item


def run_command(command: str, *, cwd: Path | None = None, silent: bool = False) -> str | None:
    """Run a shell command and return stripped stdout, or None on non-zero exit."""
    if not silent:
        print(f'> {command}')
    result = run(command, shell=True, capture_output=True, text=True, cwd=cwd or root_dir)
    if result.returncode == 0:
        return result.stdout.strip()
    if not silent:
        print(f'Out:\n{result.stdout}\nErr:\n{result.stderr}\nrc: {result.returncode}')
    return None


def run_script(script_path: Path, cmd_line_args: list[str] | None = None, check: bool = True) -> None:
    """Run a script file in the repository root, optionally passing command-line arguments."""
    command = f'{script_path.relative_to(root_dir).as_posix()} {" ".join(cmd_line_args or [])}'
    run(command, shell=True, check=check, cwd=root_dir)


def write_file(path: Path, content: bytes, msg: str | None = None) -> None:
    """Write bytes to the path, creating parent directories as needed, and optionally print a status message."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if msg is not None:
        print(f'{msg}, wrote {len(content)} bytes to {path}')


def disabled[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Decorator that disables func by raising NotImplementedError on every call."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if getenv('disabled') == 'false':
            return func(*args, **kwargs)
        raise NotImplementedError(f'{func.__name__} is disabled')

    return wrapper


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


def show_value[T](value: T) -> None:
    """Print value to stdout, formatting lists, dicts, and Paths for readability."""
    if isinstance(value, list):
        print('\n'.join(map(str, value)))
    elif isinstance(value, dict):
        print('\n'.join(f'{k}: {v!s}' for k, v in value.items()))
    elif isinstance(value, Path):
        print(value.relative_to(Path.cwd()).as_posix())
    else:
        print(str(value))


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


def upload_keys() -> None:
    """Upload changes to keys/keys.json to the remote repository via the GitHub CLI.

    Does nothing if keys/keys.json has not been modified.

    Behavior depends on whether the authenticated GitHub user is the repository owner:
      - Admin (owner): pushes directly to master.
      - Regular user:  creates a pull request from a dedicated branch
                       (keys_json_file_updated_by_<email>); the administrator
                       reviews and merges it to grant master key access.

    Requires the GitHub CLI (gh) to be authenticated (gh auth login).
    """
    if is_unchanged(keys_file):
        print('Keys/keys.json unchanged, no need to push.')
        return
    result = run_command('gh auth status || gh auth login')
    if result is None or result.strip() == '':
        print('Error: GitHub CLI (gh) is not authenticated. Please run "solver gh-login" first.')
        return
    run_script(upload_keys_to_origin, cmd_line_args=['push' if is_admin() else 'pull'])
    print('Keys/keys.json updated. Once the pull request is merged, run "solver git-merge" to refresh.')
