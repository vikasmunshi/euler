#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 337
# https://projecteuler.net/problem=337
# Answer: 
# Notes: 
import textwrap
from typing import Any, Dict

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(**kwarg: Dict[str, Any]) -> SolutionResult:
    # enter the solution here
    raise NotImplementedError


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 337
https://projecteuler.net/problem=337
Let $\{a_1, a_2, ..., a_n\}$ be an integer sequence of length $n$ such that:
$a_1 = 6$
for all $1 \le i \lt n$: $\phi(a_i) \lt \phi(a_{i + 1}) \lt a_i \lt a_{i + 1}$.1
Let $S(N)$ be the number of such sequences with $a_n \le N$.

For example, $S(10) = 4$: $\{6\}$, $\{6, 8\}$, $\{6, 8, 9\}$ and $\{6, 10\}$.

We can verify that $S(100) = 482073668$ and $S(10\,000) \bmod 10^8 = 73808307$.

Find $S(20\,000\,000) \bmod 10^8$.

1 $\phi$ denotes Euler's totient function.


''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)