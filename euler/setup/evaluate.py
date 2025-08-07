#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution evaluation for Project Euler problems."""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from itertools import product
from multiprocessing import Process, Queue
from queue import Empty
from time import perf_counter
from typing import Any, Literal

from euler.logger import logger
from euler.setup.solution_info import SolutionInfo
from euler.setup.solution_registry import Solution, get_registered_solutions
from euler.setup.test_case import TestCase, TestCaseCategory
from euler.utils.color_codes import Color
from euler.utils.human_readable_time import human_readable_seconds


def load_solution_module(info: SolutionInfo) -> Any | None:
    try:
        return import_module(info.solution_module)
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(f'Error loading solution module {e}')
        return None


def get_solution_functions(info: SolutionInfo) -> list[Solution]:
    if load_solution_module(info):
        return get_registered_solutions(info.euler_problem)
    return list()


def get_main_solution_function(info: SolutionInfo) -> Solution:
    solutions: list[Solution]
    solutions = [s for s in get_solution_functions(info) if TestCaseCategory.EXTENDED in s.__test_case_categories__]
    if len(solutions) == 0:
        solutions = [s for s in get_solution_functions(info) if TestCaseCategory.MAIN in s.__test_case_categories__]
        if len(solutions) == 0:
            raise ValueError(f'No solution found for problem {info.euler_problem} that handles the main test case')
    return solutions[0]


__show_solution__: bool = False


def show_solution() -> bool:
    return __show_solution__


def set_show_solution(show: bool) -> None:
    global __show_solution__
    __show_solution__ = show


def format_msg(status: Literal['correct', 'incorrect', 'undecided', 'info'], msg: str, euler_problem: int,
               func_name: str, test_case_category: str, kwargs_str: str, execution_time: float, ) -> str:
    tick_mark: str = {'correct': f'{Color.GREEN}✓',
                      'incorrect': f'{Color.RED}✗',
                      'undecided': f'{Color.YELLOW}?',
                      'info': f'{Color.BLUE}□', }[status]
    return (f'{tick_mark} {euler_problem:06d} {f"{test_case_category} test case":21} '
            f'[{human_readable_seconds(execution_time):>18}] {func_name}({kwargs_str}) {msg}{Color.RESET}')


@dataclass(frozen=False, kw_only=True, slots=True)
class EvaluationResult:
    failed_problems: int = field(default=0)
    failed_test_cases: int = field(default=0)
    passed_problems: int = field(default=0)
    passed_test_cases: int = field(default=0)
    recorded_test_cases: int = field(default=0)
    skipped_test_cases: int = field(default=0)
    total_execution_time_in_sec: float = field(default=0.0)
    total_problems: int = field(default=0)
    total_test_cases: int = field(default=0)
    undecided_test_cases: int = field(default=0)

    def __add__(self, other: EvaluationResult) -> EvaluationResult:
        return EvaluationResult(
                failed_problems=self.failed_problems + other.failed_problems,
                failed_test_cases=self.failed_test_cases + other.failed_test_cases,
                passed_problems=self.passed_problems + other.passed_problems,
                passed_test_cases=self.passed_test_cases + other.passed_test_cases,
                recorded_test_cases=self.recorded_test_cases + other.recorded_test_cases,
                skipped_test_cases=self.skipped_test_cases + other.skipped_test_cases,
                total_execution_time_in_sec=self.total_execution_time_in_sec + other.total_execution_time_in_sec,
                total_problems=self.total_problems + other.total_problems,
                total_test_cases=self.total_test_cases + other.total_test_cases,
                undecided_test_cases=self.undecided_test_cases + other.undecided_test_cases, )

    def __iadd__(self, other: EvaluationResult) -> EvaluationResult:
        self.failed_problems += other.failed_problems
        self.failed_test_cases += other.failed_test_cases
        self.passed_problems += other.passed_problems
        self.passed_test_cases += other.passed_test_cases
        self.recorded_test_cases += other.recorded_test_cases
        self.skipped_test_cases += other.skipped_test_cases
        self.total_execution_time_in_sec += other.total_execution_time_in_sec
        self.total_problems += other.total_problems
        self.total_test_cases += other.total_test_cases
        self.undecided_test_cases += other.undecided_test_cases
        return self

    def __format__(self, format_spec: str) -> str:
        if format_spec == 's' or format_spec == 'summary':
            msg = (f'{self.total_problems: 4d} problems:\n'
                   f'\t {self.passed_problems: 4d} passed,\n'
                   f'\t {self.failed_problems:4d} failed.\n'
                   f'{self.total_test_cases: 4d} test cases:\n'
                   f'\t {self.passed_test_cases: 4d} passed,\n'
                   f'\t {self.failed_test_cases: 4d} failed')
            if self.skipped_test_cases:
                msg += f',\n\t {self.skipped_test_cases: 4d} skipped'
            if self.undecided_test_cases:
                msg += f',\n\t {self.undecided_test_cases: 4d} undecided'
            if self.recorded_test_cases:
                msg += f',\n\t {self.recorded_test_cases: 4d} recorded'
            msg += f'.\n\nTotal Execution Time: {self.total_execution_time_in_sec:.2f}s\n'
            return msg
        else:
            return f'{self}'


def evaluate(euler_problem: int, time_out_in_seconds: int = 300,
             mode: Literal['evaluate', 'list', 'record'] = 'evaluate') -> int:
    return evaluate_and_get_evaluation_result(euler_problem, time_out_in_seconds, mode).failed_test_cases


def evaluate_and_get_evaluation_result(euler_problem: int, time_out_in_seconds: int = 300,
                                       mode: Literal['evaluate', 'list', 'record'] = 'evaluate') -> EvaluationResult:
    with SolutionInfo.from_file(euler_problem) as info:
        if not info.test_cases:
            raise ValueError(f'No test cases found for problem {info.euler_problem}')
        if mode == 'record':
            info.reset_answers()
        evaluation_result: EvaluationResult = EvaluationResult()
        evaluation_result.total_problems += 1
        for solution, test_case in product(get_solution_functions(info), info.test_cases):
            evaluation_result.total_test_cases += 1
            if test_case.test_case_category not in solution.__test_case_categories__:
                evaluation_result.skipped_test_cases += 1
                continue
            if mode == 'list':
                print(format_msg(status='info',
                                 msg='',
                                 euler_problem=info.euler_problem,
                                 func_name=solution.__name__,
                                 test_case_category=test_case.test_case_category,
                                 kwargs_str=test_case.kwargs_str,
                                 execution_time=test_case.solution_execution_time_in_sec.get(solution.__name__, 0), ))
                continue
            result, execution_time = evaluate_single_test_case(info, solution, test_case, time_out_in_seconds)
            answer: Any = test_case.result or info.test_case_answers.get(test_case.kwargs_str)
            evaluation_result.total_execution_time_in_sec += execution_time
            if mode == 'record':
                info.record_answer(test_case, result, execution_time, solution.__name__)
                print(format_msg(status='undecided',
                                 msg=f'answer recorded ({result})',
                                 euler_problem=info.euler_problem,
                                 func_name=solution.__name__,
                                 test_case_category=test_case.test_case_category,
                                 kwargs_str=test_case.kwargs_str,
                                 execution_time=execution_time, ))
                evaluation_result.recorded_test_cases += 1
            elif answer is None:
                print(format_msg(status='undecided',
                                 msg=f'= {result} (check at {info.url})',
                                 euler_problem=info.euler_problem,
                                 func_name=solution.__name__,
                                 test_case_category=test_case.test_case_category,
                                 kwargs_str=test_case.kwargs_str,
                                 execution_time=execution_time, ))
                evaluation_result.undecided_test_cases += 1
            elif answer == result:
                info.record_answer(test_case, result, execution_time, solution.__name__)
                print(format_msg(status='correct',
                                 msg=f'= {result}',
                                 euler_problem=info.euler_problem,
                                 func_name=solution.__name__,
                                 test_case_category=test_case.test_case_category,
                                 kwargs_str=test_case.kwargs_str,
                                 execution_time=execution_time, ))
                evaluation_result.passed_test_cases += 1
            else:
                print(format_msg(status='incorrect',
                                 msg=f'= {result} (expected {answer})',
                                 euler_problem=info.euler_problem,
                                 func_name=solution.__name__,
                                 test_case_category=test_case.test_case_category,
                                 kwargs_str=test_case.kwargs_str,
                                 execution_time=execution_time, ))
                evaluation_result.failed_test_cases += 1
        return evaluation_result


def evaluate_single_test_case(info: SolutionInfo, solution: Solution | None, test_case: TestCase,
                              time_out_in_seconds: int = 300) -> tuple[Any | None, float]:
    solution = solution or get_main_solution_function(info)
    return evaluate_enforce_timeout(solution, test_case, time_out_in_seconds)


def evaluate_enforce_timeout(solution: Solution, test_case: TestCase,
                             time_out_in_seconds: int) -> tuple[Any | None, float]:
    queue: Queue[Any | None] = Queue()
    process: Process = Process(target=evaluate_catch_exceptions, args=(solution, test_case, queue,))
    start_time = perf_counter()
    process.start()
    process.join(timeout=time_out_in_seconds)
    if process.is_alive():
        process.terminate()
        process.join()
    try:
        item = queue.get_nowait()
        if item is None:
            raise Empty
    except Empty:
        logger.error({'func': solution.__name__, 'test_case': test_case.kwargs_str, 'error': 'timeout error', })
        return None, perf_counter() - start_time
    else:
        result, execution_time = item
        return result, execution_time


def evaluate_catch_exceptions(solution: Solution, test_case: TestCase, queue: Queue[tuple[Any | None, float]]) -> None:
    start_time = perf_counter()
    try:
        result = solution(**test_case.kwargs)
    except Exception as e:
        logger.error({'func': solution.__name__, 'test_case': test_case.kwargs_str, 'error': e, })
        queue.put((None, perf_counter() - start_time))
    else:
        queue.put((result, perf_counter() - start_time))
