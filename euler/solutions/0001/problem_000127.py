
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 127
# https://projecteuler.net/problem=127
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 127
    https://projecteuler.net/problem=127
    The radical of $n$, $\operatorname{rad}(n)$, is the product of distinct prime factors of $n$. For example, $504 = 2^3 \times 3^2 \times 7$, so $\operatorname{rad}(504) = 2 \times 3 \times 7 = 42$.
We shall define the triplet of positive integers $(a, b, c)$ to be an abc-hit if:
$\gcd(a, b) = \gcd(a, c) = \gcd(b, c) = 1$
$a \lt b$
$a + b = c$
$\operatorname{rad}(abc) \lt c$
For example, $(5, 27, 32)$ is an abc-hit, because:
$\gcd(5, 27) = \gcd(5, 32) = \gcd(27, 32) = 1$
$5 \lt 27$
$5 + 27 = 32$
$\operatorname{rad}(4320) = 30 \lt 32$
It turns out that abc-hits are quite rare and there are only thirty-one abc-hits for $c \lt 1000$, with $\sum c = 12523$.
Find $\sum c$ for $c \lt 120000$.


    """
    raise NotImplementedError


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
