#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluator for Project Euler solutions.

This module provides functionality to evaluate the correctness of solutions to Project Euler problems
using safe concurrency by running each solution in a separate process.
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


def __run_single_evaluation__(solution: SolutionProtocol, problem_args: ProblemArgs) -> int:
    """
    Run a single evaluation of a problem solution and return 0 if correct, 1 otherwise.

    Args:
        solution: The solution function to evaluate
        problem_args: The problem arguments with the expected answer

    Returns:
        0 if the solution is correct, 1 if it's incorrect or throws an exception
    """
    func_str = f"{solution.__name__}({', '.join(f'{k}={v}' for k, v in problem_args.kwargs.items())})"
    logger.info({'action': 'evaluating_solution', 'function': solution.__name__, 'kwargs': problem_args.kwargs})

    try:
        start_time = time.time()
        result = solution(**problem_args.kwargs)
        execution_time = time.time() - start_time

        # Check if the result matches the expected answer
        is_correct = result == problem_args.answer

        # Format the output string
        status = "\033[32m✓\033[0m" if is_correct else "\033[31m✗\033[0m"
        answer_str = f" (expected: {problem_args.answer})" if not is_correct else ""

        print(f"{func_str} = {result}{answer_str} {status} [{execution_time:.6f}s]")

        logger.info({
            'action': 'evaluation_completed',
            'function': solution.__name__,
            'kwargs': problem_args.kwargs,
            'result': result,
            'expected': problem_args.answer,
            'is_correct': is_correct,
            'execution_time': execution_time
        })

        return 0 if is_correct else 1

    except Exception as e:
        print(f"\033[31mError evaluating {func_str}: {type(e).__name__}: {e}\033[0m")
        logger.error({
            'action': 'evaluation_error',
            'function': solution.__name__,
            'kwargs': problem_args.kwargs,
            'error': str(e),
            'error_type': type(e).__name__
        })
        return 1


def evaluate_solution(solution: SolutionProtocol, args_list: ProblemArgsList,
                      timeout: int, max_workers: int | None) -> int:
    """
    Evaluate a solution function with multiple problem arguments in parallel processes.

    Args:
        solution: The solution function to evaluate
        args_list: List of problem arguments with expected answers
        timeout: Maximum time in seconds to wait for each evaluation
        max_workers: Maximum number of worker processes (defaults to number of CPUs)

    Returns:
        The sum of return codes (0 if all evaluations are correct, otherwise the count of failures)
    """
    logger.info({'action': 'starting_evaluation', 'function': solution.__name__, 'problem_count': len(args_list)})

    return_code = 0

    # Use a ProcessPoolExecutor for safe concurrency
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all problems for evaluation
        future_to_problem = {executor.submit(__run_single_evaluation__, solution, problem_args): problem_args
                             for problem_args in args_list}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_problem):
            problem = future_to_problem[future]
            try:
                # Get the result with timeout
                result_code = future.result(timeout=timeout)
                return_code += result_code
            except concurrent.futures.TimeoutError:
                print(f"\033[31mTimeout after {timeout}s for {solution.__name__}({problem.kwargs})\033[0m")
                logger.error({'action': 'evaluation_timeout', 'function': solution.__name__, 'kwargs': problem.kwargs,
                              'timeout': timeout})
                return_code += 1

    # Print summary
    success_count = len(args_list) - return_code
    print(f'\n{solution.__doc__}\n\nSummary: {success_count}/{len(args_list)} correct ({return_code} failures)\n')
    logger.info({'action': 'evaluation_summary', 'function': solution.__name__, 'total': len(args_list),
                 'success': success_count, 'failures': return_code})

    return return_code


def execute_solution_module(solution_module: pathlib.Path, args: Namespace) -> int:
    log_level = args.log_level
    max_workers = args.max_workers
    problem_number = args.problem_number
    timeout = args.timeout
    logger.setLevel(log_level)
    # Run the solution module in a new Python process
    try:
        # Prepare command to run the module as a script
        cmd = f'{sys.executable} {solution_module} --log-level {log_level} --timeout {timeout}'
        if max_workers:
            cmd += f' --max-workers {max_workers}'

        # Run the solution module in a new process
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

        # Print the output
        if result.stdout:
            print(result.stdout.strip('\n'))

        # Print any errors
        if result.stderr:
            print(result.stderr.strip('\n'))

        logger.info({'action': 'solution_executed', 'problem_number': problem_number, 'return_code': result.returncode})

        return result.returncode

    except subprocess.TimeoutExpired:
        logger.error({'action': 'solution_timeout', 'problem_number': problem_number, 'timeout': timeout})
        print(f"\nError: Solution execution timed out after {timeout} seconds")
        return 124  # Standard timeout exit code

    except Exception as e:
        logger.error({'action': 'cli_error', 'error': str(e), 'error_type': type(e).__name__})
        print(f"\nError: {type(e).__name__}: {e}")
        return 1
