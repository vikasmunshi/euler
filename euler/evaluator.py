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
- __run_single_evaluation__: Executes and validates a single test case
- evaluate_solution: Coordinates parallel execution of multiple test cases
- execute_solution_module: Runs a solution module as a separate process
- module_main: Entry point for individual solution modules

Usage:
Typically used by solution modules through the module_main function, which is called 
from the __main__ block of each solution file.
"""
from __future__ import annotations

import concurrent.futures
import pathlib
import subprocess
import sys
import time
from argparse import Namespace

from euler.logger import logger
from euler.types import SolutionProtocol, ProblemArgs, ProblemArgsList


def __run_single_evaluation__(*, problem_number: int, solution: SolutionProtocol, problem_args: ProblemArgs) -> int:
    """
    Run a single evaluation of a problem solution and return 0 if correct, 1 otherwise.

    This function handles the execution of a single test case, measures its execution time,
    validates the result against the expected answer, and provides formatted output with
    colour-coded status indicators. It also handles any exceptions that may occur during execution.

    Args:
        problem_number: The Project Euler problem number for contextual reporting
        solution: The solution function to evaluate (must conform to SolutionProtocol)
        problem_args: The problem arguments with the expected answer

    Returns:
        0 if the solution is correct, 1 if it's incorrect or throws an exception

    Note:
        This function is designed to be used with ProcessPoolExecutor and should not be
        called directly from user code.
    """
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

        print(f'{status} {problem_number:06d}\033[0m {func_str} = {result}{answer_str} [{execution_time:.6f}s]')
        return 0 if is_correct else 1

    except Exception as e:
        print(f'\033[31mError evaluating {problem_number=} {func_str}: {type(e).__name__}: {e}'
              f'\033[0m')
        return 1


def evaluate_solution(*, problem_number: int, solution: SolutionProtocol, args_list: ProblemArgsList,
                      timeout: int, max_workers: int | None) -> int:
    """
    Evaluate a solution function with multiple problem arguments in parallel processes.

    This function orchestrates the concurrent execution of multiple test cases for a given 
    solution. It creates a pool of worker processes, submits each test case for evaluation,
    monitors their execution, and handles timeouts. After all evaluations are complete, it
    produces a summary of the results.

    Args:
        problem_number: The Project Euler problem number for contextual reporting
        solution: The solution function to evaluate (must conform to SolutionProtocol)
        args_list: List of problem arguments with expected answers
        timeout: Maximum time in seconds to wait for each evaluation
        max_workers: Maximum number of worker processes (defaults to number of CPUs)

    Returns:
        The sum of return codes (0 if all evaluations are correct, otherwise the count of failures)

    Note:
        This function uses ProcessPoolExecutor to achieve true parallelism, which is particularly
        beneficial for CPU-bound solution algorithms. The timeout parameter prevents hanging on
        infinite loops or extremely inefficient solutions.
    """
    return_code = 0

    # Use a ProcessPoolExecutor for safe concurrency
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all problems for evaluation
        future_to_problem = {executor.submit(__run_single_evaluation__, problem_number=problem_number,
                                             solution=solution, problem_args=problem_args): problem_args
                             for problem_args in args_list}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_problem):
            problem = future_to_problem[future]
            try:
                # Get the result with timeout
                result_code = future.result(timeout=timeout)
                return_code += 0 if result_code == 0 else 1
            except concurrent.futures.TimeoutError:
                print(f'\033[31mTimeout after {timeout}s for {problem_number:06d} ({problem.kwargs})'
                      f'\033[0m')
                return_code += 1

    # Print summary
    total_count = len(args_list)
    success_count = total_count - return_code
    status = '\033[32m✓' if return_code == 0 else '\033[31m✗'
    print(f'{status} {problem_number:06d} summary: {success_count}/{total_count} correct ({return_code} failures)'
          f'\033[0m')
    return return_code


def execute_solution_module(solution_module: pathlib.Path, args: Namespace) -> int:
    """
    Execute a solution module as a separate Python process.

    This function runs a solution module in a new process, providing isolation and preventing
    any side effects from affecting the main process. It passes command-line arguments to the
    child process and handles timeout conditions.

    Args:
        solution_module: Path to the solution module to execute
        args: Namespace containing command-line arguments (log_level, max_workers, 
              problem_number, timeout)

    Returns:
        Return code from the executed process (0 for success, non-zero for failures)

    Note:
        This function is primarily used by command-line tools that need to execute
        solutions externally rather than within the same process.
    """
    log_level = args.log_level
    max_workers = args.max_workers
    problem_number = args.problem_number
    timeout = args.timeout
    logger.setLevel(log_level.upper())
    # Prepare command to run the module as a script
    cmd = f'{sys.executable} {solution_module} --log-level {log_level} --timeout {timeout}'
    if max_workers:
        cmd += f' --max-workers {max_workers}'

    # Run the solution module in a new process
    process = subprocess.Popen(cmd.split())
    try:
        result = process.wait(timeout=timeout)
        logger.info({'action': 'solution_executed', 'problem_number': problem_number, 'return_code': result})
        return 0 if result == 0 else 1
    except subprocess.TimeoutExpired:
        logger.error({'action': 'solution_timeout', 'problem_number': problem_number, 'timeout': timeout})
        print(f'\033[31mError evaluating {problem_number=} solution execution timed out after {timeout} seconds'
              f'\033[0m')
        return 1
    except Exception as e:
        logger.error({'action': 'cli_error', 'error': str(e), 'error_type': type(e).__name__})
        print(f'\033[31mError evaluating {problem_number=} {type(e).__name__}: {e}'
              f'\033[0m')
        return 1
    finally:
        process.kill()


def module_main(module_name: str, solution: SolutionProtocol, args_list: ProblemArgsList) -> int:
    """
    Main entry point for executing a solution module directly.

    This function serves as the bridge between individual solution modules and the evaluation
    infrastructure. When a solution module is run directly, this function extracts the problem
    number from the module name, parses command-line arguments, and calls evaluate_solution
    with the appropriate parameters.

    Args:
        module_name: Name of the module (typically __file__ from the calling module)
        solution: The solution function to evaluate (must conform to SolutionProtocol)
        args_list: List of problem arguments with expected answers

    Returns:
        Return code indicating success (0) or failure (non-zero)

    Note:
        This function is designed to be called from the __main__ block of solution modules,
        typically with a pattern like:

        ```python
        if __name__ == '__main__':
            from typing import cast
            from euler.evaluator import module_main
            raise SystemExit(module_main(module_name=__file__,
                                         solution=cast(SolutionProtocol, solution),
                                         args_list=problem_args_list))
        ```
    """
    from euler.cli import parser
    problem_number: int = int(module_name.split('.')[0].split('_')[-1])
    args = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    timeout, max_workers = args.timeout, args.max_workers
    return evaluate_solution(problem_number=problem_number, solution=solution, args_list=args_list,
                             timeout=timeout, max_workers=max_workers)
