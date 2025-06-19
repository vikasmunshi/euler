
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 451
# https://projecteuler.net/problem=451
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 451
    https://projecteuler.net/problem=451
    
Consider the number $15$.

There are eight positive numbers less than $15$ which are coprime to $15$: $1, 2, 4, 7, 8, 11, 13, 14$.

The modular inverses of these numbers modulo $15$ are: $1, 8, 4, 13, 2, 11, 7, 14$
  
because

$1 \cdot 1 \bmod 15=1$

$2 \cdot 8=16 \bmod 15=1$

$4 \cdot 4=16 \bmod 15=1$

$7 \cdot 13=91 \bmod 15=1$

$11 \cdot 11=121 \bmod 15=1$

$14 \cdot 14=196 \bmod 15=1
$

Let $I(n)$ be the largest positive number $m$ smaller than $n-1$ such that the modular inverse of $m$ modulo $n$ equals $m$ itself.

So $I(15)=11$.

Also $I(100)=51$ and $I(7)=1$.


Find $\sum I(n)$ for $3 \le n \le 2 \times 10^7$.

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
