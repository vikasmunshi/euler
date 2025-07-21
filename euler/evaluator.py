#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluator for Project Euler solutions.

This module provides comprehensive functionality to evaluate the correctness and performance of
solutions to Project Euler problems. It leverages Python's concurrent processing capabilities to
safely execute solutions in parallel, optimizing evaluation time while preventing interference
between test cases.

Key Features:
1. Parallel Evaluation: Uses ProcessPoolExecutor to run multiple test cases concurrently
2. Safe Execution: Isolates each solution run in its own process to prevent side effects
3. Timeout Handling: Implements configurable timeouts to catch inefficient or infinite loops
4. Consistent Reporting: Provides standardized output formatting with colour-coded results
5. Logging Support: Integrates with the project's logging system for detailed execution tracking

Main Components:
- register_solution: Decorator that registers solution functions with their test cases
- evaluate_solutions: Coordinates parallel execution of multiple test cases
- __run_single_evaluation__: Executes and validates a single test case

Usage:
Typically used in solution modules through the register_solution decorator and evaluate_solutions function:

```python
@register_solution(problem_number=42, args_list=problem_args_list)
def my_solution(*, param1: int, param2: str) -> int:
    # Solution implementation
    return result

if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
```

The evaluator provides a consistent framework for testing solutions against multiple test cases,
with detailed performance metrics and automatic validation of results.
"""
from __future__ import annotations

import concurrent.futures
import time
from collections import defaultdict
from inspect import getsource, signature
from typing import Callable, List, ParamSpec, Set, Tuple, TypeVar

from euler.logger import logger
from euler.template import default_solution
from euler.types import ProblemArgs, ProblemArgsList

__all__ = ['evaluate_solutions', 'register_solution', 'solutions', 'show_solution']

solutions: dict[int, List[Tuple[Callable, ProblemArgsList]]] = defaultdict(list)

PS = ParamSpec("PS")  # ParamSpec to capture the parameter specification of the functions being decorated
RT = TypeVar("RT")  # TypeVar to represent the return type of the functions being decorated
FS = Callable[PS, RT]


def register_solution(*, problem_number: int, args_list: ProblemArgsList) -> Callable[[FS], FS]:
    """Register a solution function for evaluation with specified test cases.

    This decorator registers a solution function along with its test cases for later evaluation.
    It performs validation to ensure the function signature matches the parameters in the test cases.
    Only functions that are fully implemented (not raising NotImplementedError) are registered.

    Args:
        problem_number: The Project Euler problem number this solution addresses
        args_list: A list of ProblemArgs objects containing test cases with inputs and expected outputs

    Returns:
        A decorator function that registers the decorated solution function

    Raises:
        TypeError: If the function parameters don't match the parameters in the test cases

    Example:
        >>> @register_solution(problem_number=42, args_list=problem_args_list)
        >>> def solution_function(*, param1: int, param2: str) -> int:
        >>>     result = 0
        >>>     # Solution implementation
        >>>     return result
    """

    def decorator(func: FS) -> FS:
        if getsource(func).strip('\n') == default_solution:
            logger.info(f'Skipping default {func.__name__} for {problem_number=}.')
        else:
            func_kwargs: Set[str] = set(signature(func).parameters.keys())
            param_kwargs: Set[str] = set(i for item_list in (arg.kwargs.keys() for arg in args_list) for i in item_list)
            if func_kwargs != param_kwargs:
                raise TypeError(f'Function {func.__name__} args do not match problem args: '
                                f'{func_kwargs=} != {param_kwargs=}')
            solutions[problem_number].append((func, args_list))
        return func

    return decorator


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
    start_time = time.time()
    from euler.cli import parser
    args = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    timeout, max_workers = args.timeout, args.max_workers
    global __show_solution
    __show_solution = args.show_solution
    first, last = sorted((first_problem_number, last_problem_number or first_problem_number))
    # Use a ProcessPoolExecutor for safe concurrency
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all solutions for evaluation
        futures = {executor.submit(__evaluate__, problem_number, solution, problem_args): (problem_number, problem_args)
                   for problem_number in range(first, last + 1)
                   for solution, args_list in solutions[problem_number]
                   for problem_args in args_list}
        total_count: int = len(futures)
        return_code: int = 0
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            problem_number, problem_args = futures[future]
            try:
                # Get the result with timeout
                result_code = future.result(timeout=timeout)
                return_code += 0 if result_code == 0 else 1
            except concurrent.futures.TimeoutError:
                print(f'\033[31mTimeout after {timeout}s for {problem_number:06d} ({problem_args.kwargs})\033[0m')
                return_code += 1

    # Print summary
    success_count = total_count - return_code
    status = '\033[32m✓' if return_code == 0 else '\033[31m✗'
    if last_problem_number:
        execution_time = time.time() - start_time
        print(f'{status} {first_problem_number:06d} to {last_problem_number:06d} '
              f'summary: {success_count}/{total_count} correct ({return_code} failures) [{execution_time:.6f}s]\033[0m')
    else:
        print(f'{status} {first_problem_number:06d} '
              f'summary: {success_count}/{total_count} correct ({return_code} failures)\033[0m')
    return return_code


def __evaluate__(problem_number: int, solution: Callable, problem_args: ProblemArgs) -> int:
    func_str = f'{solution.__name__}({", ".join(f"{k}={v}" for k, v in problem_args.kwargs.items())})'
    try:
        start_time = time.time()
        result = solution(**problem_args.kwargs)
        execution_time = time.time() - start_time

        # Check if the result matches the expected answer
        is_correct = result == problem_args.answer

        # Format the output string
        status = '\033[32m✓' if is_correct else '\033[31m✗'
        answer_str = f' (expected: {problem_args.answer})' if not is_correct else ''
        time_str = f'\033[32m[{execution_time:.6f}s]' if execution_time < 5.0 else f'\033[31m[{execution_time:.6f}s]'

        print(f'{status} {problem_number:06d}\033[0m {func_str} = {result}{answer_str} {time_str}\033[0m')
        return 0 if is_correct else 1

    except Exception as e:
        print(f'\033[31mError evaluating {problem_number=} {func_str}: {type(e).__name__}: {e}'
              f'\033[0m')
        return 1


__show_solution: bool = False


def show_solution() -> bool:
    return __show_solution
