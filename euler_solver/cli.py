#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Literal

from euler_solver.c_libs import set_use_py_func
from euler_solver.logger import logger
from euler_solver.setup.encryption import decrypt_solution_module, encrypt_solution_module
from euler_solver.setup.evaluate import evaluate_range, set_show_solution
from euler_solver.setup.paths import get_module_path
from euler_solver.setup.register import set_evaluation_options
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
                    choices=['evaluate', 'evaluate-all', 'evaluate-dev', 'list', 'record', 'record-all'],
                    default='evaluate',
                    help='Evaluation mode (default: evaluate) evaluate: '
                         'evaluate the solutions against main test case; '
                         'evaluate-all: evaluate all test cases, considering registered test case slices;'
                         'evaluate-dev: evaluate the solutions against preliminary test cases;'
                         'list: list without evaluating solutions; '
                         'record: record correct answers and execution time; '
                         'record-all: evaluate and record all test cases, ignore registered test case slices.')
parser.add_argument('--all', '--a',
                    action='store_const',
                    dest='mode',
                    const='evaluate-all',
                    help='Short for evaluation mode evaluate-all (same as --mode evaluate-all).')
parser.add_argument('--dev', '--d',
                    action='store_const',
                    dest='mode',
                    const='evaluate-dev',
                    help='Short for evaluation mode evaluate-dev (same as --mode evaluate-dev).')
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
parser.add_argument('--use-py', '--p',
                    action='store_true',
                    default=False,
                    help='For @use_wrapped_c_function decorated functions, '
                         'use the original Python version (default: False)')
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
        from euler_solver.setup.module import get_module_idempotent
        for euler_problem in range(start_number, end_number + 1):
            py_file_path: Path = get_module_path(euler_problem)
            py_file_path_exists: bool = py_file_path.exists()
            module_fqdn: str = get_module_idempotent(euler_problem)
            print(f'Solution template for problem {euler_problem} '
                  f'{"already exists" if py_file_path_exists else "created"}: {module_fqdn}\n'
                  f'file://{py_file_path.as_posix()}')
        return 0

    if args.summary:
        create_summary()
        return 0

    mode: Literal['evaluate', 'list', 'record'] = args.mode
    match args.mode:
        case 'evaluate':
            mode = 'evaluate'
            set_evaluation_options(eval_preliminary=False, eval_main=True, eval_extended=False, ignore_slices=False)
        case 'evaluate-all':
            mode = 'evaluate'
            set_evaluation_options(eval_preliminary=True, eval_main=True, eval_extended=True, ignore_slices=True)
        case 'evaluate-dev':
            mode = 'evaluate'
            set_evaluation_options(eval_preliminary=True, eval_main=False, eval_extended=False, ignore_slices=False)
        case 'list':
            mode = 'list'
            set_evaluation_options(eval_preliminary=True, eval_main=True, eval_extended=True, ignore_slices=True)
        case 'record':
            mode = 'record'
            set_evaluation_options(eval_preliminary=False, eval_main=True, eval_extended=False, ignore_slices=False)
        case 'record-all':
            mode = 'record'
            set_evaluation_options(eval_preliminary=True, eval_main=True, eval_extended=True, ignore_slices=True)
    set_show_solution(show=args.show_solution)
    set_use_py_func(use_py_func=args.use_py)
    evaluation_result: EvaluationResult = evaluate_range(
            start_number=start_number,
            end_number=end_number,
            max_workers=args.max_workers,
            mode=mode,
            time_out_in_seconds=args.timeout,
    )
    return evaluation_result.failed_problems


if __name__ == '__main__':
    raise SystemExit(main())
