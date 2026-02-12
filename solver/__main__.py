#!/usr/bin/env python3
"""
Solver module entry point.

This module serves as the main entry point for the solver package.
"""
from __future__ import annotations

from solver.stack import stack_from_workspace, unstack_to_workspace, fill_stack


def main():
    """Main function for the solver application."""
    fill_stack(problems=[42])
    problem_number: int = 42
    unstack_to_workspace(problem_number)
    stack_from_workspace()


if __name__ == "__main__":
    raise SystemExit(main())
