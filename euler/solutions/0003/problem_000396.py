
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 396
# https://projecteuler.net/problem=396
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 396
    https://projecteuler.net/problem=396
    
For any positive integer $n$, the $n$th weak Goodstein sequence $\{g_1, g_2, g_3, ...\}$ is defined as:
 $g_1 = n$
 for $k \gt 1$, $g_k$ is obtained by writing $g_{k-1}$ in base $k$, interpreting it as a base $k + 1$ number, and subtracting $1$.

The sequence terminates when $g_k$ becomes $0$.


For example, the $6$th weak Goodstein sequence is $\{6, 11, 17, 25, ...\}$:
 $g_1 = 6$.
 $g_2 = 11$ since $6 = 110_2$, $110_3 = 12$, and $12 - 1 = 11$.
 $g_3 = 17$ since $11 = 102_3$, $102_4 = 18$, and $18 - 1 = 17$.
 $g_4 = 25$ since $17 = 101_4$, $101_5 = 26$, and $26 - 1 = 25$.

and so on.


It can be shown that every weak Goodstein sequence terminates.


Let $G(n)$ be the number of nonzero elements in the $n$th weak Goodstein sequence.

It can be verified that $G(2) = 3$, $G(4) = 21$ and $G(6) = 381$.

It can also be verified that $\sum G(n) = 2517$ for $1 \le n \lt 8$.


Find the last $9$ digits of $\sum G(n)$ for $1 \le n \lt 16$.


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
