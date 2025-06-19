
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 915
# https://projecteuler.net/problem=915
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 915
    https://projecteuler.net/problem=915
    
The function $s(n)$ is defined recursively for positive integers by 
$s(1) = 1$ and $s(n+1) = \big(s(n) - 1\big)^3 +2$ for $n\geq 1$.
 
The sequence begins: $s(1) = 1, s(2) = 2, s(3) = 3, s(4) = 10, \ldots$.


For positive integers $N$, define $$T(N) = \sum_{a=1}^N \sum_{b=1}^N \gcd\Big(s\big(s(a)\big), s\big(s(b)\big)\Big).$$  You are given $T(3) = 12$, $T(4) \equiv 24881925$ and $T(100)\equiv 14416749$ both modulo $123456789$.


Find $T(10^8)$. Give your answer modulo $123456789$.

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
