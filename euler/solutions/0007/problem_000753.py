
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 753
# https://projecteuler.net/problem=753
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 753
    https://projecteuler.net/problem=753
    Fermat's Last Theorem states that no three positive integers $a$, $b$, $c$ satisfy the equation 
$$a^n+b^n=c^n$$
for any integer value of $n$ greater than 2.

For this problem we are only considering the case $n=3$. For certain values of $p$, it is possible to solve the congruence equation:
$$a^3+b^3 \equiv c^3 \pmod{p}$$

For a prime $p$, we define $F(p)$ as the number of integer solutions to this equation for $1 \le a,b,c < p$.

You are given $F(5) = 12$ and $F(7) = 0$.

Find the sum of $F(p)$ over all primes $p$ less than $6\,000\,000$.

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
