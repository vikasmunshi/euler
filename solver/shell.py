#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

import cmd
import inspect
import shlex
from dataclasses import dataclass, field
from functools import partial, wraps
from pathlib import Path
from re import match
from subprocess import run as subprocess_run
from typing import Any, Callable

from solver.backup import backup_stack, restore_stack
from solver.crypto import SymmetricalKey, User, get_key, get_user
from solver.crypto.ops import add_keys, authorize_users
from solver.projecteuler import ProjectEulerFiles, problem_numbers
from solver.stack import stack_from_workspace, unstack_to_workspace
from solver.workspace import admin_user, clear_workspace, workspace_dir


@dataclass(frozen=True, slots=True, kw_only=True)
class Problem:
    number: int
    title: str
    difficulty: str = field(init=False)
    statement: str = field(init=False)
    path: Path = field(init=False)
    path_exists: bool = field(init=False)
    is_private: bool | None = field(init=False)

    def __post_init__(self) -> None:
        if self.number == 0:
            object.__setattr__(self, 'title', 'workspace')
            path: Path = workspace_dir
            statement: str = ''
            level: str = ''
            is_private: bool | None = None
        else:
            statement_path: Path = ProjectEulerFiles.problem_statement_md_file.stack_path(self.number)
            path = statement_path.parent
            statement = statement_path.read_text()
            level = statement.splitlines()[0].strip().split('(')[-1].strip(')')
            is_private = self.number > 100
        values = [('difficulty', level), ('statement', statement), ('path', path), ('path_exists', path.exists()),
                  ('is_private', is_private), ]
        for key, value in values:
            object.__setattr__(self, key, value)

    def __str__(self) -> str:
        return (f'{self.number:04d} - {self.title} ({self.difficulty})'
                f'{" [private]" if self.is_private else ""}')

    def __repr__(self) -> str:
        return f'Problem(number={self.number}, title="{self.title}")'


def run_cmd(cmd: str) -> str | None:
    result = subprocess_run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def continue_on_error[**P, T](func: Callable[P, T]) -> Callable[P, T | None]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print(f'{func.__name__=}, {args=}, {kwargs=}')
            print(f'Error: {err}')
            return None

    return wrapper


def email_is_valid(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return match(pattern, email) is not None


def is_callable(obj: Any) -> bool:
    return callable(obj) and not isinstance(obj, type)


def show_value[T](value: T) -> None:
    print(value)


def init() -> dict[str, Any]:
    """Initialize the shell environment."""
    problems: list[Problem] = [Problem(number=0, title='')]
    problems.extend(Problem(number=k, title=v) for k, v in problem_numbers(check_last_modified=True).items())
    in_git_repo: bool = run_cmd('git rev-parse --is-inside-work-tree') == 'true'
    gh_cli_authenticated: bool = run_cmd('gh auth status') is not None
    git_branch: str | None = run_cmd('git branch --show-current') if in_git_repo else None
    git_remote: str | None = run_cmd('git remote get-url origin') if in_git_repo else None
    git_user_email: str | None = run_cmd('git config user.email') if in_git_repo else None
    if git_user_email and not email_is_valid(git_user_email):
        git_user_email = None
    if git_branch == 'master':
        run_cmd('git fetch && git pull')
    git_status: str | None = run_cmd('git status -b --porcelain') if git_branch else None
    try:
        user: User | None = get_user()
        enc_key: SymmetricalKey | None = get_key()
        can_decrypt: bool = True
    except RuntimeError:
        user = None
        enc_key = None
        can_decrypt: bool = False
    is_admin: bool = user and (user.email == admin_user)

    def problem_number_is_valid(n: int) -> bool:
        return n in problem_numbers() and (can_decrypt or n <= 100)

    @continue_on_error
    def clear() -> None:
        """Clear the workspace."""
        clear_workspace()

    @continue_on_error
    def stack(process_deletions: bool = False) -> None:
        """Process the changes from the workspace and organizes them into the stack.

        Arguments:
            process_deletions: Indicates whether deletions in the workspace should be
                processed during the stacking operation. Defaults to False.

        Returns:
            None
        """
        stack_from_workspace(process_deletions=process_deletions)

    @continue_on_error
    def unstack(problem_number: int, *, re_init: bool = False, force_refresh: bool = False) -> None:
        """Copy a problem from stack to workspace."""
        if problem_number_is_valid(problem_number):
            unstack_to_workspace(problem_number, re_init=re_init, force_refresh=force_refresh)
        else:
            print(f'Error: Invalid problem number {problem_number}')

    if can_decrypt:
        @continue_on_error
        def backup() -> None:
            backup_stack()

        @continue_on_error
        def restore() -> None:
            restore_stack()

    if is_admin:
        @continue_on_error
        def authorize() -> None:
            authorize_users()

        @continue_on_error
        def new_keys(num: int) -> None:
            add_keys(num_new_keys=num)

    local_vars = {k: v if is_callable(v) else partial(show_value, v)
                  for k, v in locals().items() if not k.startswith('_')}
    return local_vars


def coerce(value: str, annotation: Any) -> Any:
    if annotation is bool:
        return value.lower() in ('true', '1', 'yes')
    if annotation is int:
        return int(value)
    return value


def make_do(func: Callable) -> Callable:
    sig = inspect.signature(func)
    try:
        hints = inspect.get_annotations(func, eval_str=True)
    except Exception:
        hints = {}
    pos_params = [p for p in sig.parameters.values()
                  if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]

    def do(self: Any, line: str) -> None:
        tokens = shlex.split(line)
        args: list[Any] = []
        kwargs: dict[str, Any] = {}
        pos = 0
        for token in tokens:
            if '=' in token:
                key, val = token.split('=', 1)
                norm_key = key.replace('-', '_')
                kwargs[norm_key] = coerce(val, hints.get(norm_key, str))
            elif pos < len(pos_params):
                param = pos_params[pos]
                args.append(coerce(token, hints.get(param.name, str)))
                pos += 1
        print(f'{func.__name__}({", ".join(map(str, args))}{", " if kwargs else ""}'
              f'{", ".join(f"{k}={v!r}" for k, v in kwargs.items())})')
        func(*args, **kwargs)

    do.__doc__ = func.__doc__ or str(sig)
    return do


def cli() -> int:
    local_vars = init()
    methods: dict[str, Any] = {
        'prompt': '> ',
        'do_exit': lambda self, _: True,
        'do_EOF': lambda self, _: True,
    }
    for name, func in local_vars.items():
        methods[f'do_{name}'] = make_do(func)
    Shell = type('Shell', (cmd.Cmd,), methods)
    banner = f'commands: {", ".join(sorted(local_vars.keys()))}\nType "help" or "help <command>". Ctrl-D to exit.'
    Shell().cmdloop(intro=banner)
    return 0


if __name__ == '__main__':
    raise SystemExit(cli())
