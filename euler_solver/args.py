#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import NoReturn

from euler_solver.framework.evaluate import ColorCodes
from euler_solver.framework.logger import logger

__all__ = ['parser', 'parse_args']


class EulerArgumentParser(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        print(self.format_help())
        print(f'\n{ColorCodes.RED}error: {message}{ColorCodes.RESET}\n')
        raise SystemExit(2)


usage: str = (
    '%(prog)s [-h] [-v]  problem_number [max_problem_number]\n'
    '       [--log-level {debug,info,warning,error,critical} | --debug | --info]\n'
    '       [--lock | --unlock]\n'
    '       [--setup | --summary | --mode {evaluate,evaluate-extended,evaluate-dev,list,record,record-all} |'
    ' --dev | --main | --extended | --list | --record | --record-all]\n'
    '       [--ignore-slices]\n'
    '       [--workers WORKERS]\n'
    '       [--show]\n'
    '       [--timeout TIMEOUT]\n'
    '       [--use-py]\n'
)
parser = EulerArgumentParser(
        description='CLI for retrieving Project Euler problems and evaluating solutions.',
        usage=usage,
        formatter_class=RawTextHelpFormatter,
)

parser.add_argument('-v', '--version',
                    action='version',
                    version='%(prog)s 0.2.1',
                    help='Show version number and exit\n\n')

log_group = parser.add_mutually_exclusive_group()
log_group.add_argument('--log-level',
                       choices=['debug', 'info', 'warning', 'error', 'critical'],
                       default='error',
                       help='Logging level\n'
                            'debug:    Show debug messages\n'
                            'info:     Show info messages\n'
                            'warning:  Show warning messages\n'
                            'error:    Show error messages\n'
                            'critical: Show critical messages\n'
                            'Default: error\n')
log_group.add_argument('--debug',
                       action='store_const',
                       dest='log_level',
                       const='debug',
                       help='Short for --log-level debug (same as --log debug).')
log_group.add_argument('--info',
                       action='store_const',
                       dest='log_level',
                       const='info',
                       help='Short for --log-level info (same as --log info).\n\n')

encryptions_group = parser.add_mutually_exclusive_group()
encryptions_group.add_argument('--lock',
                               action='store_true',
                               default=False,
                               help='Encrypt private solution module')
encryptions_group.add_argument('--unlock',
                               action='store_true',
                               default=False,
                               help='Decrypt encrypted private solution module\n\n')

mode_group = parser.add_mutually_exclusive_group()
mode_group.add_argument('--setup', '--n',
                        action='store_true',
                        default=False,
                        help='Create solution template for new problem (note: max async workers is capped at 8)')
mode_group.add_argument('--summary', '--p',
                        action='store_true',
                        default=False,
                        help='create summary of project euler_solver solutions\n\n')
mode_group.add_argument('--mode',
                        choices=['evaluate', 'evaluate-extended', 'evaluate-dev', 'list', 'record', 'record-all'],
                        default='evaluate',
                        help='Evaluation mode \n'
                             'evaluate:          evaluate the solutions against main test case;\n'
                             'evaluate-extended: evaluate all test cases;\n'
                             'evaluate-dev:      evaluate the solutions against dev test cases or main test case'
                             ' if no dev test cases are defined;\n'
                             'list:              list without evaluating solutions;\n'
                             'record:            record correct answers and execution time for dev and main'
                             ' test cases;\n'
                             'record-all:        evaluate and record all test cases.\n'
                             'Default: evaluate')
mode_group.add_argument('--dev', '--d',
                        action='store_const',
                        dest='mode',
                        const='evaluate-dev',
                        help='Short for evaluation mode evaluate-dev (same as --mode evaluate-dev).')
mode_group.add_argument('--main', '--m',
                        action='store_const',
                        dest='mode',
                        const='evaluate',
                        help='Short for evaluation mode evaluate (same as --mode evaluate).')
mode_group.add_argument('--extended', '--e',
                        action='store_const',
                        dest='mode',
                        const='evaluate-extended',
                        help='Short for evaluation mode evaluate-extended (same as --mode evaluate-extended).')
mode_group.add_argument('--list', '--l',
                        action='store_const',
                        dest='mode',
                        const='list',
                        help='Short for evaluation mode list (same as --mode list).')
mode_group.add_argument('--record', '--rec',
                        action='store_const',
                        dest='mode',
                        const='record',
                        help='Short for evaluation mode record (same as --mode record).')
mode_group.add_argument('--record-all', '--r',
                        action='store_const',
                        dest='mode',
                        const='record-all',
                        help='Short for evaluation mode record-all (same as --mode record-all).\n\n')

parser.add_argument('--ignore-slices', '--i',
                    action='store_true',
                    default=False,
                    help='Ignore slices in test cases')
parser.add_argument('--workers',
                    type=int,
                    default=None,
                    help='Number of worker processes, defaults to number of CPUs')
parser.add_argument('--show', '--v',
                    action='store_true',
                    default=False,
                    help='show (optional) visualization of solution')
parser.add_argument('--timeout',
                    type=int,
                    default=300,
                    help='Maximum time in seconds to wait for each evaluation')
parser.add_argument('--use-py', '--py',
                    action='store_true',
                    default=False,
                    help='For @use_wrapped_c_function decorated functions, evaluate the Python implementation')

problem_number_help = (
    'If only problem_number (required) is provided, the problem number to evaluate.\n'
    'If max_problem_number is also provided, the range of problems from problem_number through max_problem_number'
    ' (both inclusive) are evaluated.\n'
    'If problem_number is 0, problems 1 through 957 are evaluated.'
)
max_problem_number_help = (
    '(optional) last problem number (inclusive) to evaluate.\n\n'
    'Examples:\n'
    f'{parser.prog} 21       # Evaluate solution against main test case for problem 21\n'
    f'{parser.prog} 1 12 --d # Evaluate solutions against dev test cases for problems 1 through 12 (both included)\n'
    f'{parser.prog} 0        # Evaluate solutions for problems 1 through 957 (both included)\n'
)

parser.add_argument('problem_number', type=int, help=problem_number_help)
parser.add_argument('max_problem_number', type=int, nargs='?', default=None, help=max_problem_number_help)


def parse_args() -> tuple[int, int, Namespace]:
    args: Namespace = parser.parse_args()
    logger.setLevel((args.log_level or 'ERROR').upper())
    start_number: int = args.problem_number
    if args.max_problem_number is None:
        end_number: int = start_number
    else:
        start_number, end_number = sorted([start_number, args.max_problem_number])
    if start_number == 0:
        start_number, end_number = 1, 957
    return start_number, end_number, args
