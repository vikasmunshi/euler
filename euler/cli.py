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

import importlib
from argparse import ArgumentParser, Namespace

from euler.check_modules import check_modules
from euler.evaluator import evaluate_solutions, solutions
from euler.loader import get_module_path, load_problem_module, load_problem_modules, module_name
from euler.logger import logger

# Define acceptable log levels (case-insensitive to improve user experience)
log_levels = ['DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical']

# Configure the command-line argument parser with a descriptive help message
parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')

# Global configuration options that apply to both single-problem and batch modes
parser.add_argument('--log-level', choices=log_levels,
                    default='ERROR', help='Logging level (default: ERROR)')
parser.add_argument('--timeout', type=int, default=300,
                    help='Maximum time in seconds to wait for each evaluation (default: 300)')
parser.add_argument('--max-workers', type=int, default=None,
                    help='Maximum number of worker processes (default: number of CPUs)')
parser.add_argument('--show-solution', '--s', action='store_true', default=False,
                    help='show (optional) visualization of solution (default: False)')


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
    parser.add_argument('--check', '--c', action='store_true', default=False,
                        help='Check created solution modules for correctness and exit without evaluating solutions.')

    args: Namespace = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    start_number: int = args.problem_number
    if args.max_problem_number is None:
        end_number: int = start_number
    else:
        start_number, end_number = sorted([start_number, args.max_problem_number])
    if start_number == 0:
        create_if_not_exists: bool = False
        start_number, end_number = 1, 950
    else:
        create_if_not_exists = True
    if args.download:
        return load_problem_modules(start_number=start_number, end_number=end_number)
    elif args.list:
        for module in (module_name(problem_number=problem_number) for problem_number in range(1, 950)
                       if get_module_path(problem_number=problem_number).exists()):
            importlib.import_module(module)
        for problem_num, solution_specs in sorted(solutions.items()):
            print(f'Problem #{problem_num}:')
            for solution, args_list in solution_specs:
                print(f'\t- {solution.__name__} ({len(args_list)} test cases)')
        return 0
    elif args.check:
        return check_modules(first_problem_number=start_number, last_problem_number=end_number)
    else:
        for module in (module_name(problem_number=problem_num) for problem_num in range(start_number, end_number + 1)
                       if (get_module_path(problem_number=problem_num).exists()
                           or (create_if_not_exists and load_problem_module(problem_number=problem_num)))):
            importlib.import_module(module)
        return evaluate_solutions(first_problem_number=start_number, last_problem_number=end_number)


# Module entry point - executed when the script is run directly (not imported)
if __name__ == '__main__':
    # Use SystemExit to properly terminate the program with the appropriate exit code
    # This ensures the shell/OS receives the correct success/failure signal
    # (0 indicates success, non-zero indicates failure)
    raise SystemExit(main())
