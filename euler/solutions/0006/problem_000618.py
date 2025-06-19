
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 618
# https://projecteuler.net/problem=618
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 618
    https://projecteuler.net/problem=618
    Consider the numbers $15$, $16$ and $18$:

$15=3\times 5$ and $3+5=8$.

$16 = 2\times 2\times 2\times 2$ and $2+2+2+2=8$.

$18 = 2\times 3\times 3$ and $2+3+3=8$.
 

$15$, $16$ and $18$ are the only numbers that have $8$ as sum of the prime factors (counted with multiplicity).

We define $S(k)$ to be the sum of all numbers $n$ where the sum of the prime factors (with multiplicity)  of $n$ is $k$.

Hence $S(8) = 15+16+18 = 49$.

Other examples: $S(1) = 0$, $S(2) = 2$, $S(3) = 3$, $S(5) = 5 + 6 = 11$.

The Fibonacci sequence is $F_1 = 1$, $F_2 = 1$, $F_3 = 2$, $F_4 = 3$, $F_5 = 5$, ....

Find the last nine digits of $\displaystyle\sum_{k=2}^{24}S(F_k)$.


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
