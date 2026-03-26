#!/usr/bin/python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from solver.projecteuler import problem_numbers
from solver.stack import stack_from_workspace, unstack_to_workspace
from solver.crypto import check_self
from solver.workspace import backup_dir, stack_dir

__all__ = ['backup_stack', 'restore_stack']


def backup_stack() -> None:
    if not check_self():
        return
    for problem_number, title in problem_numbers().items():
        stack_path: Path = stack_dir.joinpath(*f'{problem_number:04d}')
        if not stack_path.exists():
            print(f'Info: Stack {stack_path} not found, skipping backup')
            continue
        backup_path: Path = backup_dir.joinpath(*f'{problem_number:04d}')
        unstack_to_workspace(problem_number, workspace_path=backup_path)
        print(f'Backup complete for {problem_number:04d} {title}')


def restore_stack() -> None:
    if not check_self():
        return
    for problem_number, title in problem_numbers().items():
        backup_path: Path = backup_dir.joinpath(*f'{problem_number:04d}')
        if not backup_path.exists():
            print(f'Info: Backup {backup_path} not found, skipping restore')
            continue
        stack_from_workspace(workspace_path=backup_path)
        print(f'Restore complete for {problem_number:04d} {title}')
