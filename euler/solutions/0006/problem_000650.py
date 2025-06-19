#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 650
# https://projecteuler.net/problem=650
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
solution to Project Euler problem 650
https://projecteuler.net/problem=650

Let $B(n) = \displaystyle \prod_{k=0}^n {n \choose k}$, a product of binomial coefficients.

For example, $B(5) = {5 \choose 0} \times {5 \choose 1} \times {5 \choose 2}  \times {5 \choose 3} \times {5 \choose 4} \times {5 \choose 5} = 1 \times 5 \times 10 \times 10 \times 5 \times 1 = 2500$.


Let $D(n) = \displaystyle \sum_{d|B(n)} d$, the sum of the divisors of $B(n)$.

For example, the divisors of B(5) are 1, 2, 4, 5, 10, 20, 25, 50, 100, 125, 250, 500, 625, 1250 and 2500,

so D(5) = 1 + 2 + 4 + 5 + 10 + 20 + 25 + 50 + 100 + 125 + 250 + 500 + 625 + 1250 + 2500 = 5467.


Let $S(n) = \displaystyle \sum_{k=1}^n D(k)$.

You are given $S(5) = 5736$, $S(10) = 141740594713218418$ and $S(100)$ mod $1\,000\,000\,007 = 332792866$.


Find $S(20\,000)$ mod $1\,000\,000\,007$.



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