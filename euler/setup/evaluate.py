#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution evaluation for Project Euler problems."""
from __future__ import annotations

from importlib import import_module
from json import dump, load
from multiprocessing import Process, Queue
from queue import Empty
from time import perf_counter
from types import ModuleType
from typing import Any, Literal

from euler.logger import logger
from euler.setup.module import get_module, record_answer_in_module
from euler.setup.register import Solution, framework_version
from euler.setup.result import EvaluationResult
from euler.utils.color_codes import Color
from euler.utils.human_readable_time import human_readable_seconds

__show_solution__: bool = False


def show_solution() -> bool:
    return __show_solution__


def set_show_solution(show: bool) -> None:
    global __show_solution__
    __show_solution__ = show


def get_solution_functions(euler_problem: int, *, force_recreate: bool = False) -> list[Solution]:
    try:
        module: ModuleType = import_module(get_module(euler_problem, force_recreate=force_recreate))
        assert module.framework_version == framework_version, f'{module.framework_version=} != {framework_version=},'
        euler_solutions_registry = getattr(module, 'euler_solutions_registry')
        if isinstance(euler_solutions_registry, list):
            return euler_solutions_registry
        else:
            return []
    except (AssertionError, AttributeError, ImportError, ModuleNotFoundError) as e:
        logger.error(f'No solution {framework_version=} for problem {euler_problem}, error={e}')
        return []


def evaluate(euler_problem: int, *,
             time_out_in_seconds: int = 300,
             mode: Literal['evaluate', 'list', 'record'] = 'evaluate',
             force_recreate: bool = False,
             ) -> int:
    evaluation_result: EvaluationResult = evaluate_and_get_evaluation_result(euler_problem,
                                                                             time_out_in_seconds=time_out_in_seconds,
                                                                             mode=mode,
                                                                             force_recreate=force_recreate)
    return evaluation_result.failed_test_cases


def evaluate_and_get_evaluation_result(euler_problem: int, *,
                                       time_out_in_seconds: int = 300,
                                       mode: Literal['evaluate', 'list', 'record'] = 'evaluate',
                                       func_def_len: int | None = None,
                                       force_recreate: bool = False,
                                       ) -> EvaluationResult:
    implemented_solutions: list[Solution] = get_solution_functions(euler_problem, force_recreate=force_recreate)
    if not implemented_solutions:
        return EvaluationResult(failed_problems=1, passed_problems=-1, total_problems=1)
    test_case_answers: dict[str, Any] = load(implemented_solutions[0].test_case_answers_file.open('r'))
    if mode == 'record':
        test_case_answers = {key: answer
                             for solution in implemented_solutions
                             for key, answer in test_case_answers.items()
                             for test_case in solution.test_cases
                             if test_case['key'] == key}
    evaluation_result: EvaluationResult = EvaluationResult()
    evaluation_result.total_problems += 1
    if func_def_len is None:
        func_def_len = max(len(f'{solution.__name__}({test_case['key']})')
                           for solution in implemented_solutions
                           for test_case in solution.test_cases)
    for solution, test_case in ((solution, test_case)
                                for solution in implemented_solutions
                                for test_case in solution.test_cases):
        evaluation_result.total_test_cases += 1
        answer_key: str = test_case['key']
        answer: Any = test_case_answers.get(answer_key)
        et_key: str = test_case['et_key']
        func_def = f'{f"{solution.__name__}({answer_key})":<{func_def_len}}'
        if mode == 'list':
            print(format_msg(status='info',
                             msg='' if answer is None else f'= {answer}',
                             euler_problem=solution.euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=test_case_answers.get(et_key, ''), ))
            continue
        result, execution_time = evaluate_enforce_timeout(solution, test_case, time_out_in_seconds)
        evaluation_result.total_execution_time_in_sec += execution_time
        if result is None:
            print(format_msg(status='incorrect',
                             msg=f'= {result} (check at {solution.url})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=execution_time, ))
            evaluation_result.failed_test_cases += 1
        elif mode == 'record':
            if test_case_answers.get(answer_key) is None:
                test_case_answers[answer_key] = result
            test_case_answers[et_key] = human_readable_seconds(execution_time)
            if not solution.is_private and test_case['category'] == 'main':
                record_answer_in_module(euler_problem, result)
            print(format_msg(status='undecided',
                             msg=f'answer recorded ({result})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=execution_time, ))
            evaluation_result.recorded_test_cases += 1
        elif answer is None:
            print(format_msg(status='undecided',
                             msg=f'= {result} (check at {solution.url})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=execution_time, ))
            evaluation_result.undecided_test_cases += 1
        elif answer == result:
            print(format_msg(status='correct',
                             msg=f'= {result}',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=execution_time, ))
            evaluation_result.passed_test_cases += 1
        else:
            print(format_msg(status='incorrect',
                             msg=f'= {result} (expected {answer})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case['category'],
                             execution_time=execution_time, ))
            evaluation_result.failed_test_cases += 1
    if mode == 'record':
        test_case_answers = {k: v for k, v in sorted(test_case_answers.items())}
        dump(test_case_answers, implemented_solutions[0].test_case_answers_file.open('w'), indent=4)
    return evaluation_result


def evaluate_enforce_timeout(solution: Solution, test_case: dict[str, Any],
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
        logger.error({'func': solution.__name__, 'test_case': test_case['key'], 'error': 'timeout error', })
        return None, perf_counter() - start_time
    else:
        result, execution_time = item
        return result, execution_time


def evaluate_catch_exceptions(solution: Solution, test_case: dict[str, Any],
                              queue: Queue[tuple[Any | None, float]]) -> None:
    start_time = perf_counter()
    try:
        result = solution(**test_case['input'])
    except Exception as e:
        logger.error({'func': solution.__name__, 'test_case': test_case['key'], 'error': e, })
        queue.put((None, perf_counter() - start_time))
    else:
        queue.put((result, perf_counter() - start_time))


def format_msg(*, status: Literal['correct', 'incorrect', 'undecided', 'info'], msg: str, euler_problem: int,
               func_def: str, test_case_category: str, execution_time: float | str, ) -> str:
    tick_mark: str = {'correct': f'{Color.GREEN}✓',
                      'incorrect': f'{Color.RED}✗',
                      'undecided': f'{Color.YELLOW}?',
                      'info': f'{Color.BLUE}□', }[status]
    if isinstance(execution_time, float):
        execution_time = human_readable_seconds(execution_time)
    if len(msg) > 128:
        msg = f'{msg[:128]}...'
    return (f'{tick_mark} {euler_problem:06d} {f"{test_case_category} test case":21} '
            f'[{execution_time:>18}] {func_def} {msg}{Color.RESET}')
