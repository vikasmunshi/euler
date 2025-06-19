
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 801
# https://projecteuler.net/problem=801
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 801
    https://projecteuler.net/problem=801
    The positive integral solutions of the equation $x^y=y^x$ are $(2,4)$, $(4,2)$ and $(k,k)$ for all $k > 0$.

For a given positive integer $n$, let $f(n)$ be the number of integral values $0 < x,y \leq n^2-n$ such that
$$x^y\equiv y^x \pmod n.$$
For example, $f(5)=104$ and $f(97)=1614336$.

Let $S(M,N)=\sum f(p)$ where the sum is taken over all primes $p$ satisfying $M\le p\le N$.

You are given $S(1,10^2)=7381000$ and $S(1,10^5) \equiv 701331986 \pmod{993353399}$.

Find $S(10^{16}, 10^{16}+10^6)$. Give your answer modulo $993353399$.

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
