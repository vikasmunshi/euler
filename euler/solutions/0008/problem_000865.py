#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 865
# https://projecteuler.net/problem=865
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
solution to Project Euler problem 865
https://projecteuler.net/problem=865

A triplicate number is a positive integer such that, after repeatedly removing three consecutive identical digits from it, all its digits can be removed.


For example, the integer $122555211$ is a triplicate number:
$$122{\color{red}555}211 \rightarrow 1{\color{red}222}11\rightarrow{\color{red}111}\rightarrow.$$
On the other hand, neither $663633$ nor $9990$ are triplicate numbers.


Let $T(n)$ be how many triplicate numbers are less than $10^n$.


For example, $T(6) = 261$ and $T(30) = 5576195181577716$.


Find $T(10^4)$. Give your answer modulo $998244353$.

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