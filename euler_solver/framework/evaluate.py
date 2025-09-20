#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution evaluation for Project Euler problems."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from enum import StrEnum
from json import dump
from math import isnan, nan
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from time import perf_counter
from typing import Any

from euler_solver.framework.file_lock import FileLock
from euler_solver.framework.loader import load_locked_module, record
from euler_solver.framework.logger import logger
from euler_solver.framework.paths import get_evaluation_log_path, get_module_path
from euler_solver.framework.register import Solution, SolutionRegistry, Status, TestCase, get_func_def, get_registry
from euler_solver.framework.result import ColorCodes, EvaluationResult

__show_solution__: bool = False


class Mode(StrEnum):
    evaluate = 'evaluate'
    list = 'list'
    record = 'record'


def show_solution() -> bool:
    return __show_solution__


def set_show_solution(show: bool) -> None:
    global __show_solution__
    __show_solution__ = show


def evaluate(euler_problem: int, *,
             mode: Mode = Mode.evaluate,
             time_out_in_seconds: int = 300, ) -> int:
    evaluation_result: EvaluationResult = evaluate_and_get_evaluation_result(
            euler_problem,
            func_def_len=None,
            time_out_in_seconds=time_out_in_seconds,
            mode=mode,
    )
    return evaluation_result.failed_test_cases


def evaluate_range(start_number: int, end_number: int, *,
                   mode: Mode = Mode.evaluate,
                   num_workers: int | None,
                   time_out_in_seconds: int = 300, ) -> EvaluationResult:
    evaluation_result = EvaluationResult()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        kwargs_list: list[dict[str, Any]] = [{'euler_problem': euler_problem,
                                              'func_def_len': 121,
                                              'time_out_in_seconds': time_out_in_seconds,
                                              'mode': mode, }
                                             for euler_problem in range(start_number, end_number + 1)]
        futures = {executor.submit(evaluate_and_get_evaluation_result, **kwargs): kwargs['euler_problem']
                   for kwargs in kwargs_list}
        for future in as_completed(futures):
            euler_problem: int = futures[future]
            try:
                result = future.result()
                if result.undecided_test_cases != 0:
                    result.unsolved_problems += result.total_problems
                    result.unsolved_problems_list.append(euler_problem)
                elif result.failed_test_cases != 0:
                    evaluation_result.failed_problems += result.total_problems
                    evaluation_result.failed_problems_list.append(euler_problem)
                else:
                    evaluation_result.passed_problems += result.total_problems
                    evaluation_result.passed_problems_list.append(euler_problem)
                evaluation_result += result
            except Exception as e:
                evaluation_result.total_problems += 1
                evaluation_result.failed_problems += 1
                evaluation_result.failed_problems_list.append(euler_problem)
                num_test_cases = len(instance.test_cases) if (instance := get_registry(euler_problem)) else 0
                evaluation_result.total_test_cases += num_test_cases
                evaluation_result.failed_test_cases += num_test_cases
                logger.error({'action': 'evaluation error', 'euler_solver problem': euler_problem, 'error': e})

    logger.info({'evaluation summary': f'{evaluation_result:summary}'})
    print(f'{ColorCodes.BLUE if evaluation_result.failed_test_cases == 0 else ColorCodes.RED}\n{"#" * 32}\n'
          f'Evaluation summary: \n{evaluation_result:s}{"#" * 32}\n{ColorCodes.RESET}')
    return evaluation_result


def evaluate_and_get_evaluation_result(euler_problem: int, *,
                                       func_def_len: int | None,
                                       mode: Mode = Mode.evaluate,
                                       time_out_in_seconds: int = 300, ) -> EvaluationResult:
    if load_locked_module(euler_problem) is None:
        raise RuntimeError(f'No solution for problem {euler_problem}.')
    registry: SolutionRegistry | None = SolutionRegistry.get(euler_problem)
    if registry is None or len(registry.solutions) == 0 or len(registry.test_cases) == 0:
        raise RuntimeError(f'No test case for problem {euler_problem}.')
    evaluation_result: EvaluationResult = EvaluationResult(total_problems=1)
    func_def_len = func_def_len or (max(len(func_def) for func_def in registry.evaluation_log.keys()) + 1)
    for test_case, solution in ((tc, s) for s in registry.solutions for tc in s.test_cases):
        evaluation_result.total_test_cases += 1
        func_def = get_func_def(test_case, solution.__name__)
        if mode == Mode.list:
            result: Any = test_case.answer
            execution_time: float = registry.get_execution_time(func_def)
        else:
            result, execution_time = evaluate_enforce_timeout(solution, test_case, time_out_in_seconds)
            if result is NotImplemented:
                execution_time = float('nan')
            registry.set_execution_time(func_def, execution_time)
        status: Status = test_case.check_answer(answer=result, record=mode == 'record')
        print_and_tabulate(
                evaluation_result=evaluation_result,
                execution_time=execution_time,
                func_def=f'{func_def:<{func_def_len}}',
                mode=mode,
                registry=registry,
                result=result,
                status=status,
                test_case=test_case,
        )
    if mode == 'record':
        with FileLock(get_evaluation_log_path(euler_problem), 'write') as f:
            dump(registry.evaluation_log, f, indent=2)
        if registry.unsolved_test_cases:
            py_file: Path | None = record(euler_problem, registry.test_cases)
            logger.info({'action': 'Answers Recorded', 'euler_problem': euler_problem, 'file': py_file})
    return evaluation_result


def evaluate_enforce_timeout(solution: Solution, test_case: TestCase,
                             time_out_in_seconds: int) -> tuple[Any | None, float]:
    queue: Queue[Any | None] = Queue()
    process: Process = Process(target=evaluate_catch_exceptions, args=(solution, test_case, queue,))
    start_time = perf_counter()
    process.start()
    process.join(timeout=time_out_in_seconds)
    no_result_error: str = 'killed'
    if process.is_alive():
        no_result_error = 'timeout'
        process.terminate()
        process.join()
    try:
        item = queue.get_nowait()
        if item is None:
            raise Empty
    except Empty:
        logger.error({'func': solution.__name__, 'test_case': test_case, 'return_code': process.exitcode,
                      'error': no_result_error, })
        return None, perf_counter() - start_time
    else:
        result, execution_time = item
        return result, execution_time


def evaluate_catch_exceptions(solution: Solution, test_case: TestCase,
                              queue: Queue[tuple[Any | None, float]]) -> None:
    start_time = perf_counter()
    try:
        result = solution(**test_case.input)
    except NotImplementedError:
        queue.put((NotImplemented, perf_counter() - start_time))
    except Exception as e:
        logger.error({'func': solution.__name__, 'test_case': test_case, 'error': e, })
        queue.put((None, perf_counter() - start_time))
    else:
        queue.put((result, perf_counter() - start_time))


def print_and_tabulate(*,
                       evaluation_result: EvaluationResult,
                       execution_time: float,
                       func_def: str,
                       mode: Mode,
                       registry: SolutionRegistry,
                       result: Any,
                       status: Status,
                       test_case: TestCase,
                       ) -> None:
    evaluation_result.total_execution_time_in_sec += execution_time
    match mode, status:
        case Mode.list, _:
            print_msg(
                    et_str=human_readable_seconds(execution_time),
                    euler_problem=registry.euler_problem,
                    func_def=func_def,
                    msg=f'{ColorCodes.RED}  unsolved' if status == Status.unsolved else f'= {test_case.answer}',
                    status=status,
                    test_case_category=test_case.category,
            )
            if status == Status.unsolved:
                evaluation_result.undecided_test_cases += 1
            else:
                evaluation_result.passed_test_cases += 1
        case _, Status.unsolved:
            print_msg(
                    et_str='NotImplemented  ',
                    euler_problem=registry.euler_problem,
                    func_def='',
                    msg=f'file://{get_module_path(registry.euler_problem)}',
                    status=status,
                    test_case_category=test_case.category,
            )
            evaluation_result.undecided_test_cases += 1
        case Mode.record, _:
            print_msg(
                    et_str=human_readable_seconds(execution_time),
                    euler_problem=registry.euler_problem,
                    func_def=func_def,
                    msg=f'answer recorded ({result})',
                    status=status,
                    test_case_category=test_case.category,
            )
            evaluation_result.recorded_test_cases += 1
        case _, Status.correct:
            print_msg(
                    et_str=human_readable_seconds(execution_time),
                    euler_problem=registry.euler_problem,
                    func_def=func_def,
                    msg=f'= {result}',
                    status=status,
                    test_case_category=test_case.category,
            )
            evaluation_result.passed_test_cases += 1
        case _, Status.incorrect:
            print_msg(
                    et_str=human_readable_seconds(execution_time),
                    euler_problem=registry.euler_problem,
                    func_def=func_def,
                    msg=f'= {result} (expected {test_case.answer})',
                    status=status,
                    test_case_category=test_case.category,
            )
            evaluation_result.failed_test_cases += 1
        case _, Status.undecided:
            print_msg(
                    et_str=human_readable_seconds(execution_time),
                    euler_problem=registry.euler_problem,
                    func_def=func_def,
                    msg=f'= {result} (check at {registry.url})',
                    status=status,
                    test_case_category=test_case.category,
            )
            evaluation_result.undecided_test_cases += 1


def print_msg(*,
              et_str: str,
              euler_problem: int,
              func_def: str,
              msg: str,
              status: Status,
              test_case_category: str,
              ) -> None:
    tick_mark: str = {Status.correct: f'{ColorCodes.GREEN}✓',
                      Status.recorded: f'{ColorCodes.BLUE}□',
                      Status.incorrect: f'{ColorCodes.RED}✗',
                      Status.undecided: f'{ColorCodes.YELLOW}?',
                      Status.unsolved: f'{ColorCodes.ORANGE}□',
                      }[status]
    if len(msg) > 128:
        msg = f'{msg[:128]}...'
    print(f'{tick_mark} {euler_problem:06d} {f"{test_case_category} test case":21} '
          f'[{et_str:>18}] {func_def} {msg}{ColorCodes.RESET}')


def human_readable_seconds(seconds: float) -> str:
    if isnan(seconds):
        return '-'
    if seconds < 0:
        return f'-{human_readable_seconds(-seconds)}'
    if seconds >= 1:
        return f'{seconds:.2f} sec'
    elif seconds >= 1e-3:
        return f'{seconds * 1e3:.2f} milli-sec'
    elif seconds >= 1e-6:
        return f'{seconds * 1e6:.2f} micro-sec'
    else:
        return f'{seconds * 1e9:.2f} nano-sec'


def seconds_from_human_readable(human_readable: str) -> float:
    if human_readable:
        num, suffix = human_readable.split(' ', maxsplit=1)
        multiplier = {'sec': 1, 'milli-sec': 1e3, 'micro-sec': 1e6, 'nano-sec': 1e9}[suffix.strip()]
        return float(num) / multiplier
    else:
        return nan
