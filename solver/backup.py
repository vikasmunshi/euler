#!/usr/bin/python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from solver.projecteuler import problem_numbers
from solver.stack import stack_from_workspace, unstack_to_workspace
from solver.crypto import default_key_is_valid
from solver.workspace import BACKUP_DIR, STACK_DIR

__all__ = ['backup_stack', 'restore_stack']


def backup_stack() -> None:
    if not default_key_is_valid():
        print('Error: Key not found/invalid, run key_exchange first')
        return
    for problem_number, title in problem_numbers().items():
        stack_dir: Path = STACK_DIR.joinpath(*f'{problem_number:04d}')
        if not stack_dir.exists():
            print(f'Info: Stack directory {stack_dir} not found, skipping backup')
            continue
        backup_dir: Path = BACKUP_DIR.joinpath(*f'{problem_number:04d}')
        unstack_to_workspace(problem_number, workspace_dir=backup_dir)
        print(f'Backup complete for {problem_number:04d} {title}')


def restore_stack() -> None:
    if not default_key_is_valid():
        print('Error: Key not found/invalid, run key_exchange first')
        return
    for problem_number, title in problem_numbers().items():
        backup_dir: Path = BACKUP_DIR.joinpath(*f'{problem_number:04d}')
        if not backup_dir.exists():
            print(f'Info: Backup directory {backup_dir} not found, skipping restore')
            continue
        stack_from_workspace(workspace_dir=backup_dir)
        print(f'Restore complete for {problem_number:04d} {title}')
