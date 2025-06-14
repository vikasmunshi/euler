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
    parser.add_argument('problem_number', type=int, help='The number of the Project Euler problem to retrieve')
    parser.add_argument('max_problem_number', type=int, nargs='?', default=None,
                        help='The maximum number of the Project Euler problem to retrieve (default: problem_number)')
    args: Namespace = parser.parse_args()
    logger.setLevel(args.log_level)
    logger.info({'action': 'cli_start', 'message': 'Starting Project Euler CLI',
                 'problem_number': args.problem_number, 'timeout': args.timeout, 'max_workers': args.max_workers})
    if args.max_problem_number:
        modules_list = get_problem_modules(start_number=args.problem_number, end_number=args.max_problem_number + 1)
        print(f'retrieved {len(modules_list)} problem modules')
        return 0
    return execute_solution_module(solution_module=get_problem_module(args.problem_number), args=args)


if __name__ == '__main__':
    exit_code: int = main()
    raise SystemExit(exit_code)
