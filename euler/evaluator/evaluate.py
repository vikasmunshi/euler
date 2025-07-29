#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" """
from __future__ import annotations

import concurrent.futures
from time import perf_counter
from typing import Any, Callable

from euler.evaluator.register import solutions
from euler.logger import logger
from euler.setup.problems import ProblemInfo, TestCase

__all__ = ['evaluate_solutions']

_show_solution: bool = False


def show_solution() -> bool:
    return _show_solution


def evaluate_solutions(first_problem_number: int, last_problem_number: int | None = None) -> int:
    """Evaluate registered solutions within a specified problem number range.

    This function coordinates the parallel execution of all registered solution functions
    for problems within the specified range. It handles timeout detection, logging,
    and provides a summary of results.

    Args:
        first_problem_number: The first problem number to evaluate
        last_problem_number: The last problem number to evaluate (inclusive).
                            If None, only evaluates first_problem_number.

    Returns:
        An integer return code: 0 for all tests passing, or the count of failed tests

    Example:
        >>> # Evaluate a single problem
        >>> evaluate_solutions(42)
        >>> # Evaluate a range of problems
        >>> evaluate_solutions(40, 50)
        >>> evaluate_solutions(first_problem_number=40, last_problem_number=50)
    """
    start_time = perf_counter()
    from euler.cli import parser
    args = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    timeout, max_workers = args.timeout, args.max_workers
    first, last = sorted((first_problem_number, last_problem_number or first_problem_number))
    if args.show_solution:
        global _show_solution
        _show_solution = True
    # Use a ProcessPoolExecutor for safe concurrency
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all solutions for evaluation
        futures = {
            executor.submit(__evaluate_test_cases, problem_number=problem_number,
                            solution=solution, test_cases=test_cases): (problem_number, test_cases)
            for problem_number in range(first, last + 1)
            for solution, test_cases in solutions[problem_number]}
        total_count: int = len(futures)
        return_code: int = 0
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            problem_number, test_cases = futures[future]
            try:
                # Get the result with timeout
                result_code: int = future.result(timeout=timeout)
                return_code += 0 if result_code == 0 else 1
            except concurrent.futures.TimeoutError:
                print(f'\033[31mTimeout after {timeout}s for {problem_number:06d} ({test_cases})\033[0m')
                return_code += 1

    # Print summary
    success_count = total_count - return_code
    status = '\033[32m✓' if return_code == 0 else '\033[31m✗'
    if last_problem_number:
        execution_time = perf_counter() - start_time
        print(f'{status} {first_problem_number:06d} to {last_problem_number:06d} '
              f'summary: {success_count}/{total_count} correct ({return_code} failures) [{execution_time:.6f}s]\033[0m')
    else:
        print(f'{status} {first_problem_number:06d} '
              f'summary: {success_count}/{total_count} correct ({return_code} failures)\033[0m')
    return return_code


def __evaluate_test_cases(problem_number: int, solution: Callable, test_cases: list[TestCase]) -> int:
    info: ProblemInfo = ProblemInfo.from_yaml(problem_number=problem_number)
    orig_hash: str = ''.join(f'{t.solved}{t.solution_execution_time}' for t in info.test_cases)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(__evaluate_test_case, problem_number, solution, test_case, ): (i, test_case)
            for i, test_case in enumerate(test_cases)}
        return_code: int = 0
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            i, test_case = futures[future]
            # Get the result with timeout
            result: TestCase | None = future.result()
            if result:
                info.test_cases[i] = result
            else:
                return_code = 1
    if return_code == 0:
        new_hash: str = ''.join(f'{t.solved}{t.solution_execution_time}' for t in info.test_cases)
        if new_hash != orig_hash:
            if next((t.solved for t in info.test_cases if t.is_main_case), None):
                object.__setattr__(info, 'solved', True)
            info.to_yaml()
    return return_code


def __evaluate_test_case(problem_number: int, solution: Callable, test_case: TestCase) -> TestCase | None:
    """Evaluate a single solution function for a single test case."""
    func_str = f'{solution.__name__}({", ".join(f"{k}={v}" for k, v in test_case.kwargs.items())})'
    try:
        start_time = perf_counter()
        result = solution(**test_case.kwargs)
        total_time = perf_counter() - start_time
    except Exception as e:
        print(f'\033[31mError evaluating {problem_number=} {func_str}: {type(e).__name__}: {e}\033[0m')
        logger.exception(f'Error evaluating {problem_number=} {func_str}: {type(e).__name__}: {e}')
        return None
    else:
        return __record(problem_number, func_str, result, total_time, test_case)


def __record(problem_number: int, func_str: str, result: Any, total_time: float, test_case: TestCase) -> TestCase:
    answer = test_case.answer
    is_main_case = test_case.is_main_case
    is_correct, is_timely = result == answer, total_time < 1.0
    answer_str = f'{result}' if is_correct else f'{result} (expected: {answer})'
    message = (f'{"\033[32m✓" if is_correct else "\033[31m✗"} {problem_number:06d} {func_str} = {answer_str} '
               f'{"(main case)" if is_main_case else "(test case)"} [{total_time:.6f}s]\033[0m')
    print(message)
    (logger.error if not is_correct else logger.info if is_timely else logger.warning)(
        {'problem_number': problem_number, 'test_case': func_str, 'answer': answer_str, 'time': total_time,
         'is_correct': is_correct, 'is_timely': is_timely, 'is_main_case': is_main_case, })
    if is_correct:
        if (test_case.solved is False or
                test_case.solution_execution_time is None or
                total_time < test_case.solution_execution_time):
            object.__setattr__(test_case, 'solved', True)
            object.__setattr__(test_case, 'solution_execution_time', total_time)
    return test_case
