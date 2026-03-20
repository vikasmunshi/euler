#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Solver module entry point.

This module serves as the main entry point for the solver package.
"""
from __future__ import annotations

from pathlib import Path

from solver.projecteuler import problem_numbers
from solver.stack import read_stack_file, stack_from_workspace, unstack_to_workspace
from solver.workspace import WORKSPACE_DIR, clear_workspace, write_file


def main():
    test_file: Path = WORKSPACE_DIR / 'test_file.txt'
    for problem_number in problem_numbers(check_validity=True).keys():
        print(f'Processing problem {problem_number}...')
        clear_workspace()
        stack_from_workspace()
        unstack_to_workspace(problem_number, re_init=True, force_refresh=False)
        print('Expect an error about workspace already existing.')
        unstack_to_workspace(problem_number + 1)
        write_file(test_file, b"No matter what, nobody can take away the dances you've danced.")
        stack_from_workspace(process_deletions=False)
        try:
            print(read_stack_file(problem_number, test_file.name).decode())
        except FileNotFoundError:
            print(f'File {test_file.name} not found in stack')
        except (ValueError, TypeError, UnicodeError) as e:
            print(f'Error reading file {test_file.name}, skipping. error: {e}')
        test_file.unlink(missing_ok=True)
        stack_from_workspace(process_deletions=True)
        clear_workspace()
        print('Expect an error about file not found in stack.')
        read_stack_file(problem_number, test_file.name)
        print('Expect an error about file not found in stack.')


if __name__ == "__main__":
    raise SystemExit(main())
