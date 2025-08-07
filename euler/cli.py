#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

from euler.logger import logger
from euler.setup import EvaluationResult, SolutionInfo, evaluate_and_get_evaluation_result, set_show_solution
from euler.utils.color_codes import Color

__all__ = ['main', 'parser']

log_levels = ['DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical']

parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')

parser.add_argument('--list', '--l',
                    action='store_true',
                    default=False,
                    help='List created solution modules and exit without evaluating solutions.')
parser.add_argument('--log-level',
                    choices=log_levels,
                    default='ERROR',
                    help='Logging level (default: ERROR)')
parser.add_argument('--mode',
                    choices=['evaluate', 'record'],
                    default='evaluate',
                    help='Evaluation mode (default: evaluate) '
                         'evaluate: evaluate the solutions; '
                         'record: record the solution results as answers')
parser.add_argument('--record',
                    action='store_const',
                    dest='mode',
                    const='record',
                    help='Short for evaluation mode record (same as --mode record).')
parser.add_argument('--max-workers',
                    type=int,
                    default=None,
                    help='Maximum number of worker processes (default: number of CPUs)')
parser.add_argument('--show-solution', '--s',
                    action='store_true',
                    default=False,
                    help='show (optional) visualization of solution (default: False)')
parser.add_argument('--timeout',
                    type=int,
                    default=300,
                    help='Maximum time in seconds to wait for each evaluation (default: 300)')


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
    logger.setLevel(args.log_level.upper())
    start_number: int = args.problem_number
    if args.max_problem_number is None:
        end_number: int = start_number
    else:
        start_number, end_number = sorted([start_number, args.max_problem_number])
    if start_number == 0:
        start_number, end_number = 1, 950
    set_show_solution(show=args.show_solution)
    if args.list:
        evaluation_result: EvaluationResult = EvaluationResult()
        for euler_problem in range(start_number, end_number + 1):
            evaluation_result += evaluate_and_get_evaluation_result(euler_problem, mode='list')
        print(f'{evaluation_result:summary}')
        return 0
    else:
        evaluation_result = EvaluationResult()
        time_out_in_seconds, mode = args.timeout, args.mode
        with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            kwargs: list[dict[str, Any]] = [{'euler_problem': euler_problem,
                                             'time_out_in_seconds': time_out_in_seconds,
                                             'mode': mode, }
                                            for euler_problem in range(start_number, end_number + 1)]
            futures = {executor.submit(evaluate_and_get_evaluation_result, **kwarg): kwarg['euler_problem']
                       for kwarg in kwargs}
            for future in as_completed(futures):
                euler_problem = futures[future]
                try:
                    result = future.result()
                    if result.failed_test_cases == 0:
                        evaluation_result.passed_problems += 1
                    else:
                        evaluation_result.failed_problems += 1
                    evaluation_result += result
                except Exception as e:
                    evaluation_result.failed_problems += 1
                    info = SolutionInfo.from_file(euler_problem)
                    evaluation_result.failed_test_cases += len(info.test_cases)
                    logger.error({'action': 'evaluation error', 'euler problem': euler_problem, 'error': e})
        logger.info({'evaluation summary': f'{evaluation_result:summary}'})

        print(f'{Color.BLUE if evaluation_result.failed_test_cases == 0 else Color.RED}\n{"#" * 32}\n'
              f'Evaluation summary: \n{evaluation_result:s}{"#" * 32}\n{Color.RESET}')
    return evaluation_result.failed_problems + evaluation_result.failed_test_cases


# Module entry point - executed when the script is run directly (not imported)
if __name__ == '__main__':
    # Use SystemExit to properly terminate the program with the appropriate exit code
    # This ensures the shell/OS receives the correct success/failure signal
    # (0 indicates success, non-zero indicates failure)
    raise SystemExit(main())
