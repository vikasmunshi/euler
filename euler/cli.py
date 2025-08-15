#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Literal

from euler.logger import logger
from euler.setup import (EvaluationResult, create_summary, decrypt_solution_module, encrypt_solution_module,
                         evaluate_and_get_evaluation_result, get_test_cases_from_module, set_record_all_test_cases,
                         set_show_solution)
from euler.utils.color_codes import Color

__all__ = ['main', 'parser']

log_levels = ['DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical']

parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')

parser.add_argument('--debug',
                    action='store_const',
                    dest='log_level',
                    const='DEBUG',
                    help='Short for --log-level DEBUG (same as --log debug).')
parser.add_argument('--decrypt',
                    action='store_true',
                    default=False,
                    help='Decrypt encrypted private solution module (default: False)')
parser.add_argument('--encrypt',
                    action='store_true',
                    default=False,
                    help='Encrypt private solution module (default: False)')
parser.add_argument('--force-recreate', '--recreate',
                    action='store_true',
                    default=False,
                    help='Force recreation of solution templates (default: False)')
parser.add_argument('--info',
                    action='store_const',
                    dest='log_level',
                    const='INFO',
                    help='Short for --log-level INFO (same as --log info).')
parser.add_argument('--list', '--l',
                    action='store_true',
                    default=False,
                    help='List created solution modules and exit without evaluating solutions.')
parser.add_argument('--log-level', '--log',
                    choices=log_levels,
                    default='ERROR',
                    help='Logging level (default: ERROR)')
parser.add_argument('--max-workers',
                    type=int,
                    default=None,
                    help='Maximum number of worker processes (default: number of CPUs)')
parser.add_argument('--mode',
                    choices=['evaluate', 'record'],
                    default='evaluate',
                    help='Evaluation mode (default: evaluate) evaluate: '
                         'evaluate the solutions; '
                         'record: record correct answers and execution time.')
parser.add_argument('--record',
                    action='store_const',
                    dest='mode',
                    const='record',
                    help='Short for evaluation mode record (same as --mode record).')
parser.add_argument('--record-all-test-cases', '--record-all',
                    action='store_true',
                    default=False,
                    help='Record all test cases (default: False)')
parser.add_argument('--show-solution', '--s',
                    action='store_true',
                    default=False,
                    help='show (optional) visualization of solution (default: False)')
parser.add_argument('--summary', '--sum',
                    action='store_true',
                    default=False,
                    help='create summary of project euler solutions (default: False)')
parser.add_argument('--timeout',
                    type=int,
                    default=300,
                    help='Maximum time in seconds to wait for each evaluation (default: 300)')
parser.add_argument('--version',
                    action='version',
                    version='%(prog)s 0.2.1')


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
    logger.setLevel((args.log_level or 'ERROR').upper())
    start_number: int = args.problem_number
    if args.max_problem_number is None:
        end_number: int = start_number
    else:
        start_number, end_number = sorted([start_number, args.max_problem_number])
    if start_number == 0:
        start_number, end_number = 1, 957
    if args.summary:
        create_summary()
        return 0
    if args.decrypt:
        for euler_problem in range(start_number, end_number + 1):
            decrypt_solution_module(euler_problem)
        return 0
    if args.encrypt:
        for euler_problem in range(start_number, end_number + 1):
            encrypt_solution_module(euler_problem)
        return 0
    if args.list:
        evaluation_result: EvaluationResult = EvaluationResult()
        for euler_problem in range(start_number, end_number + 1):
            try:
                evaluation_result += evaluate_and_get_evaluation_result(euler_problem, mode='list')
            except Exception as e:
                evaluation_result = update_evaluation_result_on_failure(euler_problem, evaluation_result)
                logger.error({'action': 'evaluation error', 'euler problem': euler_problem, 'error': e})
        print(f'{evaluation_result:summary}')
        return evaluation_result.failed_problems
    else:
        evaluation_result = EvaluationResult()
        force_recreate: bool = args.force_recreate
        mode: Literal['evaluate', 'record'] = args.mode
        time_out_in_seconds: int = args.timeout
        set_show_solution(show=args.show_solution)
        if args.record_all_test_cases:
            mode = 'record'
            set_record_all_test_cases(True)
        with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            kwargs_list: list[dict[str, Any]] = [{'euler_problem': euler_problem,
                                                  'time_out_in_seconds': time_out_in_seconds,
                                                  'mode': mode,
                                                  'func_def_len': None if start_number == end_number else 121,
                                                  'force_recreate': force_recreate, }
                                                 for euler_problem in range(start_number, end_number + 1)]
            futures = {executor.submit(evaluate_and_get_evaluation_result, **kwargs): kwargs['euler_problem']
                       for kwargs in kwargs_list}
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
                    evaluation_result = update_evaluation_result_on_failure(euler_problem, evaluation_result)
                    logger.error({'action': 'evaluation error', 'euler problem': euler_problem, 'error': e})
        logger.info({'evaluation summary': f'{evaluation_result:summary}'})

        print(f'{Color.BLUE if evaluation_result.failed_test_cases == 0 else Color.RED}\n{"#" * 32}\n'
              f'Evaluation summary: \n{evaluation_result:s}{"#" * 32}\n{Color.RESET}')
    return evaluation_result.failed_problems


def update_evaluation_result_on_failure(euler_problem: int, evaluation_result: EvaluationResult) -> EvaluationResult:
    evaluation_result.total_problems += 1
    evaluation_result.failed_problems += 1
    num_test_cases = len(get_test_cases_from_module(euler_problem))
    evaluation_result.total_test_cases += num_test_cases
    evaluation_result.failed_test_cases += num_test_cases
    return evaluation_result


# Module entry point - executed when the script is run directly (not imported)
if __name__ == '__main__':
    # Use SystemExit to properly terminate the program with the appropriate exit code
    # This ensures the shell/OS receives the correct success/failure signal
    # (0 indicates success, non-zero indicates failure)
    raise SystemExit(main())
