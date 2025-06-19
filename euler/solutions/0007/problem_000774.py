
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 774
# https://projecteuler.net/problem=774
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 774
    https://projecteuler.net/problem=774
    Let '$\&$' denote the bitwise AND operation.

For example, $10\,\&\, 12 = 1010_2\,\&\, 1100_2 = 1000_2 = 8$.

We shall call a finite sequence of non-negative integers $(a_1, a_2, \ldots, a_n)$ conjunctive if $a_i\,\&\, a_{i+1} \neq 0$ for all $i=1\ldots n-1$.

Define $c(n,b)$ to be the number of conjunctive sequences of length $n$ in which all terms are $\le b$.
You are given that $c(3,4)=18$, $c(10,6)=2496120$, and $c(100,200) \equiv 268159379 \pmod {998244353}$.

Find $c(123,123456789)$. Give your answer modulo $998244353$.

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
