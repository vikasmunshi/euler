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

import concurrent.futures
from argparse import ArgumentParser, Namespace

from euler.evaluator import execute_solution_module
from euler.loader import get_problem_module
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
    args: Namespace = parser.parse_args()
    logger.setLevel(args.log_level)
    # Batch processing mode: evaluate multiple problems in parallel
    if args.max_problem_number:
        # Ensure start_number is always the smaller value for proper range handling
        start_number, stop_number = sorted((args.problem_number, args.max_problem_number))

        # Use ProcessPoolExecutor for parallel execution of solution evaluations
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            # Create a mapping of Future objects to their corresponding problem numbers
            # This allows us to track which result belongs to which problem
            workers = {executor.submit(execute_solution_module,
                                       # Get or create the solution module for this problem number
                                       solution_module=get_problem_module(problem_number),
                                       # Pass through all CLI arguments to each worker
                                       args=Namespace(log_level=args.log_level, max_workers=args.max_workers,
                                                      problem_number=problem_number, timeout=args.timeout, )
                                       ): problem_number
                       for problem_number in range(start_number, stop_number + 1)}

            # Initialize the cumulative return code to track overall success/failure
            return_code: int = 0

            # Process results as they complete (in any order)
            for future in concurrent.futures.as_completed(workers):
                problem_number = workers[future]
                try:
                    # Get the result of this specific problem evaluation
                    result_code = future.result(timeout=args.timeout)
                    # Increment return_code by the result_code if success (0), or by 1 if failure
                    return_code += result_code if result_code == 0 else 1
                except concurrent.futures.TimeoutError:
                    # Handle case where a solution evaluation exceeds the timeout limit
                    print(f'\033[31mTimeout after {args.timeout}s for {problem_number:06d}\033[0m')
                    return_code += 1
        # Calculate summary statistics for the batch execution
        total_count = stop_number - start_number + 1  # Total number of problems evaluated
        success_count = total_count - return_code     # Number of successful evaluations

        # Create a color-coded status indicator: green checkmark for success, red X for failures
        status = '\033[32m✓' if return_code == 0 else '\033[31m✗'

        # Format a summary message showing success ratio and failure count
        # The '\033[0m' code resets terminal colors after the message
        message = f'{status} overall summary: {success_count}/{total_count} correct ({return_code} failures)' \
                  f'\033[0m'

        # Create a decorative border around the summary message for better visibility
        line = '#' * len(message)

        # Print the formatted summary report
        print(line, message, line, sep='\n')

        # Return the cumulative return code (0 for complete success, otherwise number of failures)
        return return_code
    return execute_solution_module(solution_module=get_problem_module(args.problem_number), args=args)


# Module entry point - executed when the script is run directly (not imported)
if __name__ == '__main__':
    # Call the main function and store its return value as the exit code
    exit_code: int = main()

    # Use SystemExit to properly terminate the program with the appropriate exit code
    # This ensures the shell/OS receives the correct success/failure signal
    # (0 indicates success, non-zero indicates failure)
    raise SystemExit(exit_code)
