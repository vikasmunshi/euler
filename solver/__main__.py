#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Solver module entry point.

This module serves as the main entry point for the solver package.
"""
from __future__ import annotations

from solver.projecteuler import cache_stack
from solver.stack import stack_from_workspace, unstack_to_workspace, verify_manifest, get_stack_dir


def main():
    """Main function for the solver application."""
    problem_number: int = 1
    cache_stack(problems=[problem_number])
    unstack_to_workspace(problem_number)
    stack_from_workspace()
    print(verify_manifest(get_stack_dir(problem_number)))


if __name__ == "__main__":
    raise SystemExit(main())
