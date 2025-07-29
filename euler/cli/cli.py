#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command line interface for Project Euler problems.

This module provides a command line interface for retrieving Project Euler problems,
creating solution templates, and evaluating the correctness of implemented solutions.

The CLI supports several modes of operation:

1. Single Problem Evaluation:
   When invoked with a single problem number, the CLI will evaluate the solution for that
   specific problem against its test cases.

   Example: `euler 21` - Evaluates solution for problem #21

2. Batch Problem Evaluation:
   When invoked with a range (start and end problem numbers), the CLI will evaluate
   solutions for all problems in that range using parallel processing.

   Example: `euler 1 10` - Evaluates solutions for problems #1 through #10

3. Solution Template Creation:
   When used for a problem without an existing solution, the CLI will fetch the problem
   statement from the Project Euler website and create a solution template file in the
   appropriate location.

All operations support various configuration options including:
- Logging level control
- Execution timeout limits
- Parallel processing worker count control

The module integrates with the loader, evaluator, and logger components to provide
a seamless interface for working with Project Euler problems.
"""
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from importlib import import_module

from euler.evaluator import evaluate_solutions, solutions
from euler.logger import logger
from euler.setup import ProblemInfo, canonical_name

# Define acceptable log levels (case-insensitive to improve user experience)
log_levels = ['DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical']

# Configure the command-line argument parser with a descriptive help message
parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')

# Global configuration options that apply to both single-problem and batch modes
parser.add_argument(
    '--log-level',
    choices=log_levels,
    default='ERROR',
    help='Logging level (default: ERROR)'
)
parser.add_argument(
    '--timeout',
    type=int,
    default=300,
    help='Maximum time in seconds to wait for each evaluation (default: 300)'
)
parser.add_argument(
    '--max-workers',
    type=int,
    default=None,
    help='Maximum number of worker processes (default: number of CPUs)'
)
parser.add_argument(
    '--show-solution',
    '--s',
    action='store_true',
    default=False,
    help='show (optional) visualization of solution (default: False)'
)


def main() -> int:
    """Main entry point for the CLI.

    This function handles the command-line argument parsing and orchestrates the execution
    flow based on the provided arguments. It supports two primary modes of operation:

    1. Single Problem Mode:
       When only 'problem_number' is provided, the function evaluates the solution
       for that specific problem.

    2. Range Mode:
       When both 'problem_number' and 'max_problem_number' are provided, the function
       evaluates solutions for all problems in the range using parallel processing
       via ProcessPoolExecutor.

    In Range Mode, the function also provides a summary of results, indicating how many
    solutions were correct out of the total, along with color-coded status indicators.

    The function handles timeouts for individual problem evaluations and aggregates
    the results to determine the overall success or failure status.

    Configuration parameters (logging level, timeout duration, max worker count) are
    passed through to the solution execution context.

    Returns:
        int: Exit code (0 for complete success, non-zero indicates the number of failed evaluations)
              This return value is suitable for use as a process exit code.
    """
    problem_number_help = (
        'The problem number to evaluate the solution for. '
        'If only this argument is provided, the solution for the specified problem will be evaluated.'
    )

    max_problem_number_help = (
        'The maximum problem number in a range to download problem statements and create solution templates. '
        'If both "problem_number" and "max_problem_number" are provided, problem statements for the range '
        'will be downloaded and solution templates created.'
    )
    parser.add_argument('problem_number', type=int, help=problem_number_help)
    parser.add_argument('max_problem_number', type=int, nargs='?', default=None, help=max_problem_number_help)
    parser.add_argument('--list', '--l', action='store_true', default=False,
                        help='List created solution modules and exit without evaluating solutions.')
    parser.add_argument('--download', '--d', action='store_true', default=False,
                        help='Retrieve problem statement from Project Euler website and create solution module.')
    parser.add_argument('--sync', action='store_true', default=False,
                        help='Sync test cases and results between yaml and python files.')

    args: Namespace = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    start_number: int = args.problem_number
    if args.max_problem_number is None:
        end_number: int = start_number
    else:
        start_number, end_number = sorted([start_number, args.max_problem_number])
    if start_number == 0:
        start_number, end_number = 1, 950
    if args.download:
        logger.setLevel('INFO')
        _ = [ProblemInfo.load(first=start_number, last=end_number, refresh='missing')]
        return 0
    elif args.list:
        for problem_number in range(start_number, end_number + 1):
            module_name = f'euler.{canonical_name(problem_number, connector=".")}'
            import_module(module_name)
        for problem_number, solution_specs in sorted(solutions.items()):
            print(f'Problem #{problem_number}:')
            for solution, test_cases in solution_specs:
                print(f'\t- {solution.__name__} ({len(test_cases)} test cases)')
        return 0
    elif args.sync:
        logger.setLevel('INFO')
        for problem_info in ProblemInfo.load(first=start_number, last=end_number, refresh='never'):
            problem_info.sync(direction='auto')
        return 0
    else:
        for problem_number in range(start_number, end_number + 1):
            module_name = f'euler.{canonical_name(problem_number, connector=".")}'
            import_module(module_name)
        return evaluate_solutions(first_problem_number=start_number, last_problem_number=end_number)


# Module entry point - executed when the script is run directly (not imported)
if __name__ == '__main__':
    # Use SystemExit to properly terminate the program with the appropriate exit code
    # This ensures the shell/OS receives the correct success/failure signal
    # (0 indicates success, non-zero indicates failure)
    raise SystemExit(main())
