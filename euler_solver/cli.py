#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Literal

from euler_solver.logger import logger
from euler_solver.setup.encryption import decrypt_solution_module, encrypt_solution_module
from euler_solver.setup.evaluate import evaluate_range
from euler_solver.setup.register import SolutionRegistry
from euler_solver.setup.result import EvaluationResult
from euler_solver.setup.summary import create_summary

__all__ = ['main', 'parser']

log_levels = ['DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical']

parser = ArgumentParser(description='CLI for retrieving Project Euler problems and evaluating solutions.')

parser.add_argument('--log-level', '--log',
                    choices=log_levels,
                    default='ERROR',
                    help='Logging level (default: ERROR)')
parser.add_argument('--debug',
                    action='store_const',
                    dest='log_level',
                    const='DEBUG',
                    help='Short for --log-level DEBUG (same as --log debug).')
parser.add_argument('--info',
                    action='store_const',
                    dest='log_level',
                    const='INFO',
                    help='Short for --log-level INFO (same as --log info).')
parser.add_argument('--decrypt',
                    action='store_true',
                    default=False,
                    help='Decrypt encrypted private solution module (default: False)')
parser.add_argument('--encrypt',
                    action='store_true',
                    default=False,
                    help='Encrypt private solution module (default: False)')
parser.add_argument('--max-workers',
                    type=int,
                    default=None,
                    help='Maximum number of worker processes (default: number of CPUs)')
parser.add_argument('--mode',
                    choices=['evaluate', 'evaluate-all', 'list', 'record', 'record-all'],
                    default='evaluate',
                    help='Evaluation mode (default: evaluate) evaluate: '
                         'evaluate the solutions against main test case; '
                         'evaluate-all: evaluate all test cases, considering registered test case slices;'
                         'list: list without evaluating solutions; '
                         'record: record correct answers and execution time; '
                         'record-all: evaluate and record all test cases, ignore registered test case slices.')
parser.add_argument('--all', '--a',
                    action='store_const',
                    dest='mode',
                    const='evaluate-all',
                    help='Short for evaluation mode evaluate-all (same as --mode evaluate-all).')
parser.add_argument('--list', '--l',
                    action='store_const',
                    dest='mode',
                    const='list',
                    help='Short for evaluation mode list (same as --mode list).')
parser.add_argument('--record',
                    action='store_const',
                    dest='mode',
                    const='record',
                    help='Short for evaluation mode record (same as --mode record).')
parser.add_argument('--record-all',
                    action='store_const',
                    dest='mode',
                    const='record-all',
                    help='Short for evaluation mode record-all-test-cases (same as --mode record-all).')
parser.add_argument('--setup',
                    action='store_true',
                    default=False,
                    help='Create solution template for new problem (default: False)')
parser.add_argument('--show-solution', '--s',
                    action='store_true',
                    default=False,
                    help='show (optional) visualization of solution (default: False)')
parser.add_argument('--summary', '--sum',
                    action='store_true',
                    default=False,
                    help='create summary of project euler_solver solutions (default: False)')
parser.add_argument('--timeout',
                    type=int,
                    default=300,
                    help='Maximum time in seconds to wait for each evaluation (default: 300)')
parser.add_argument('--version',
                    action='version',
                    version='%(prog)s 0.2.1')


def main() -> int:
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
    if args.decrypt:
        for euler_problem in range(start_number, end_number + 1):
            decrypt_solution_module(euler_problem)
        return 0
    if args.encrypt:
        for euler_problem in range(start_number, end_number + 1):
            encrypt_solution_module(euler_problem)
        return 0
    if args.setup:
        from euler_solver.setup.module import get_module
        for euler_problem in range(start_number, end_number + 1):
            module_fqdn: str = get_module(euler_problem)
            print(f'Created solution template for problem {euler_problem}: {module_fqdn}')
        return 0
    if args.summary:
        create_summary()
        return 0
    if args.mode == 'evaluate-all':
        mode: Literal['evaluate', 'list', 'record'] = 'evaluate'
        SolutionRegistry.ignore_non_main_test_cases = False
    elif args.mode == 'record-all':
        mode = 'record'
        SolutionRegistry.ignore_test_case_slices = True
        SolutionRegistry.ignore_non_main_test_cases = False
    else:
        mode = args.mode
    evaluation_result: EvaluationResult = evaluate_range(start_number, end_number,
                                                         mode=mode,
                                                         time_out_in_seconds=args.timeout,
                                                         max_workers=args.max_workers, )
    return evaluation_result.failed_problems


if __name__ == '__main__':
    raise SystemExit(main())
