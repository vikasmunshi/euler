#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Solver module entry point.

This module serves as the main entry point for the solver package.
"""
from __future__ import annotations

from shutil import rmtree

from solver.projecteuler import PROBLEMS
from solver.stack import Stack
from solver.workspace import clear_workspace, WORKSPACE_DIR, STACK_DIR


def main():
    """Main function for the solver application."""
    rmtree(STACK_DIR, ignore_errors=True)
    for problem in PROBLEMS[99:101]:
        clear_workspace()
        print('#' * 64)
        stack = Stack(problem)
        stack.unstack_to_workspace()
        (WORKSPACE_DIR / 'text.file').write_text('sample text')
        stack.update_stack_from_workspace()
        print(stack.verify())
        clear_workspace()
        stack.unstack_to_workspace()
        (WORKSPACE_DIR / 'text.file').unlink()
        stack.update_stack_from_workspace(process_deletions=True)
        print(Stack(problem).verify())
        print('#' * 64, '\n')


if __name__ == "__main__":
    raise SystemExit(main())
