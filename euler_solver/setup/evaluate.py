#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution evaluation for Project Euler problems."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from importlib import import_module
from json import dump
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from time import perf_counter
from typing import Any, Literal

from euler_solver.logger import logger
from euler_solver.setup.encryption import encrypt_solution_module
from euler_solver.setup.file_lock import FileLock
from euler_solver.setup.paths import MAX_SHARABLE, get_module_fqdn, get_module_path
from euler_solver.setup.patterns import answer_re, stubber_re
from euler_solver.setup.register import Solution, SolutionRegistry, TestCase, get_registry
from euler_solver.setup.result import EvaluationResult
from euler_solver.utils.color_codes import Color
from euler_solver.utils.human_readable_time import human_readable_seconds, seconds_from_human_readable

__show_solution__: bool = False


def show_solution() -> bool:
    return __show_solution__


def set_show_solution(show: bool) -> None:
    global __show_solution__
    __show_solution__ = show


def evaluate(euler_problem: int, *,
             mode: Literal['evaluate', 'list', 'record'] = 'evaluate',
             time_out_in_seconds: int = 300,
             ) -> int:
    evaluation_result: EvaluationResult = evaluate_and_get_evaluation_result(euler_problem,
                                                                             time_out_in_seconds=time_out_in_seconds,
                                                                             mode=mode, )
    return evaluation_result.failed_test_cases


def evaluate_range(start_number: int, end_number: int, *,
                   max_workers: int | None,
                   mode: Literal['evaluate', 'list', 'record'] = 'evaluate',
                   time_out_in_seconds: int = 300,
                   ) -> EvaluationResult:
    evaluation_result = EvaluationResult()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        kwargs_list: list[dict[str, Any]] = [{'euler_problem': euler_problem,
                                              'time_out_in_seconds': time_out_in_seconds,
                                              'mode': mode,
                                              'func_def_len': None if start_number == end_number else 121, }
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
    print(f'{Color.BLUE if evaluation_result.failed_test_cases == 0 else Color.RED}\n{"#" * 32}\n'
          f'Evaluation summary: \n{evaluation_result:s}{"#" * 32}\n{Color.RESET}')
    return evaluation_result


def evaluate_and_get_evaluation_result(euler_problem: int, *,
                                       func_def_len: int | None = None,
                                       mode: Literal['evaluate', 'list', 'record'] = 'evaluate',
                                       time_out_in_seconds: int = 300,
                                       ) -> EvaluationResult:
    try:
        import_module(get_module_fqdn(euler_problem))
    except ModuleNotFoundError:
        return EvaluationResult()
    registry: SolutionRegistry | None = get_registry(euler_problem)
    if registry is None or len(registry.solutions) == 0 or len(registry.test_cases) == 0:
        return EvaluationResult()
    evaluation_result: EvaluationResult = EvaluationResult(total_problems=1)
    if func_def_len is None:
        func_def_len = max(len(tc.execution_time_key(s)) for tc in registry.test_cases for s in registry.solutions) + 1
    for test_case, solution in ((tc, s) for s in registry.solutions for tc in s.test_cases):
        evaluation_result.total_test_cases += 1
        answer: Any = test_case.answer
        func_def = f'{f"{solution.__name__}({test_case.key})":<{func_def_len}}'
        if mode == 'list':
            et_key: str = test_case.execution_time_key(solution)
            execution_time = seconds_from_human_readable(registry.test_case_answers.get(et_key, ''))
            print_and_tabulate(answer=answer,
                               euler_problem=euler_problem,
                               evaluation_result=evaluation_result,
                               execution_time=execution_time,
                               func_def=func_def,
                               mode=mode,
                               registry=registry,
                               result=answer,
                               solution=solution,
                               test_case=test_case,
                               url=registry.url, )
        else:
            result, execution_time = evaluate_enforce_timeout(solution, test_case, time_out_in_seconds)
            print_and_tabulate(answer=answer,
                               euler_problem=euler_problem,
                               evaluation_result=evaluation_result,
                               execution_time=execution_time,
                               func_def=func_def,
                               mode=mode,
                               registry=registry,
                               result=result,
                               solution=solution,
                               test_case=test_case,
                               url=registry.url, )
    if mode == 'record':
        valid_keys: set[str] = {tc.key for tc in registry.test_cases}
        valid_keys.update({tc.execution_time_key(s) for s in registry.solutions for tc in registry.test_cases})
        test_case_answers = {k: v for k, v in sorted(registry.test_case_answers.items()) if k in valid_keys}
        with FileLock(registry.test_case_answers_file, 'write') as f:
            dump(test_case_answers, f, indent=4)
        answer = next((test_case_answers[tc.key] for tc in registry.test_cases if tc.category == 'main'), '...')
        record_answer_in_module(euler_problem, str(answer))
    return evaluation_result


def evaluate_enforce_timeout(solution: Solution, test_case: TestCase,
                             time_out_in_seconds: int) -> tuple[Any | None, float]:
    queue: Queue[Any | None] = Queue()
    process: Process = Process(target=evaluate_catch_exceptions, args=(solution, test_case, queue,))
    start_time = perf_counter()
    process.start()
    process.join(timeout=time_out_in_seconds)
    no_result_error: Literal['timeout', 'killed'] = 'killed'
    if process.is_alive():
        no_result_error = 'timeout'
        process.terminate()
        process.join()
    try:
        item = queue.get_nowait()
        if item is None:
            raise Empty
    except Empty:
        logger.error({'func': solution.__name__, 'test_case': test_case.key, 'return_code': process.exitcode,
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
        logger.error({'func': solution.__name__, 'test_case': test_case.key, 'error': e, })
        queue.put((None, perf_counter() - start_time))
    else:
        queue.put((result, perf_counter() - start_time))


def print_and_tabulate(*,
                       answer: Any | None,
                       euler_problem: int,
                       evaluation_result: EvaluationResult,
                       execution_time: float,
                       func_def: str,
                       mode: Literal['evaluate', 'list', 'record'],
                       registry: SolutionRegistry,
                       result: Any,
                       solution: Solution,
                       test_case: TestCase,
                       url: str,
                       ) -> None:
    evaluation_result.total_execution_time_in_sec += execution_time
    match mode:
        case _ if result is NotImplemented:
            print(format_msg(status='unsolved',
                             msg=f'file://{get_module_path(solution.euler_problem)}',
                             euler_problem=euler_problem,
                             func_def='',
                             test_case_category=test_case.category,
                             execution_time='NotImplemented  ', ))
            evaluation_result.undecided_test_cases += 1

        case 'list':
            print(format_msg(status='info',
                             msg=f'{Color.RED}  unsolved' if answer is None else f'= {answer}',
                             euler_problem=registry.euler_problem,
                             func_def=func_def,
                             test_case_category=test_case.category,
                             execution_time=execution_time, ))
            if answer is None:
                evaluation_result.undecided_test_cases += 1
            else:
                evaluation_result.passed_test_cases += 1

        case 'record':
            if registry.test_case_answers.get(test_case.key) is None:
                registry.test_case_answers[test_case.key] = result
            et_key = test_case.execution_time_key(solution)
            registry.test_case_answers[et_key] = human_readable_seconds(execution_time)
            print(format_msg(status='undecided',
                             msg=f'answer recorded ({result})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case.category,
                             execution_time=execution_time, ))
            evaluation_result.recorded_test_cases += 1

        case _ if answer is None:
            print(format_msg(status='undecided',
                             msg=f'= {result} (check at {url})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case.category,
                             execution_time=execution_time, ))
            evaluation_result.undecided_test_cases += 1

        case _ if answer == result:
            print(format_msg(status='correct',
                             msg=f'= {result}',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case.category,
                             execution_time=execution_time, ))
            evaluation_result.passed_test_cases += 1

        case _:  # default case (answer != result)
            print(format_msg(status='incorrect',
                             msg=f'= {result} (expected {answer})',
                             euler_problem=euler_problem,
                             func_def=func_def,
                             test_case_category=test_case.category,
                             execution_time=execution_time, ))
            evaluation_result.failed_test_cases += 1


def format_msg(*, status: Literal['correct', 'incorrect', 'undecided', 'unsolved', 'info'],
               msg: str,
               euler_problem: int,
               func_def: str,
               test_case_category: str,
               execution_time: float | str, ) -> str:
    tick_mark: str = {'correct': f'{Color.GREEN}✓',
                      'incorrect': f'{Color.RED}✗',
                      'undecided': f'{Color.YELLOW}?',
                      'unsolved': f'{Color.ORANGE}□',
                      'info': f'{Color.BLUE}□', }[status]
    if isinstance(execution_time, float):
        execution_time = human_readable_seconds(execution_time)
    if len(msg) > 128:
        msg = f'{msg[:128]}...'
    return (f'{tick_mark} {euler_problem:06d} {f"{test_case_category} test case":21} '
            f'[{execution_time:>18}] {func_def} {msg}{Color.RESET}')


def record_answer_in_module(euler_problem: int, answer: str) -> None:
    py_file_path: Path = get_module_path(euler_problem)
    with FileLock(py_file_path, 'read') as f:
        source_code: str = f.read()
    stub_code: str = stubber_re.sub(r'\1 ...\n\n', answer_re.sub('Answer: ...', source_code))
    pyi_file_path: Path = py_file_path.with_suffix('.pyi')
    with FileLock(pyi_file_path, 'write') as f:
        f.write(stub_code)
    source_code_with_answer: str = answer_re.sub(f'Answer: {answer!s}', source_code)
    with FileLock(py_file_path, 'write') as f:
        f.write(source_code_with_answer)
    if euler_problem > MAX_SHARABLE:
        encrypt_solution_module(euler_problem)
