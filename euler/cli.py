#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command line interface for Project Euler problems.

This module provides a command line interface for retrieving Project Euler problems
and evaluating the correctness of coded solutions.
"""
from __future__ import annotations

from argparse import ArgumentParser, Namespace

from euler.evaluator import execute_solution_module
from euler.loader import get_problem_module, get_problem_modules
from euler.logger import logger

parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')
parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    default='ERROR', help='Logging level (default: ERROR)')
parser.add_argument('--timeout', type=int, default=300,
                    help='Maximum time in seconds to wait for each evaluation (default: 300)')
parser.add_argument('--max-workers', type=int, default=None,
                    help='Maximum number of worker processes (default: number of CPUs)')


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        int: Exit code, 0 for success
    """
    problem_number_help = (
        "The problem number to evaluate the solution for. "
        "If only this argument is provided, the solution for the specified problem will be evaluated."
    )

    max_problem_number_help = (
        "The maximum problem number in a range to download problem statements and create solution templates. "
        "If both 'problem_number' and 'max_problem_number' are provided, problem statements for the range "
        "will be downloaded and solution templates created."
    )
    parser.add_argument('problem_number', type=int, help=problem_number_help)
    parser.add_argument('max_problem_number', type=int, nargs='?', default=None, help=max_problem_number_help)
    args: Namespace = parser.parse_args()
    logger.setLevel(args.log_level)
    if args.max_problem_number:
        modules_list = get_problem_modules(start_number=args.problem_number, end_number=args.max_problem_number + 1)
        print(f'retrieved {len(modules_list)} problem modules')
        return 0
    return execute_solution_module(solution_module=get_problem_module(args.problem_number), args=args)


if __name__ == '__main__':
    exit_code: int = main()
    raise SystemExit(exit_code)
