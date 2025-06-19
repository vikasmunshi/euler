
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 778
# https://projecteuler.net/problem=778
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 778
    https://projecteuler.net/problem=778
    
If $a,b$ are two nonnegative integers with decimal representations $a=(... a_2a_1a_0)$ and $b=(... b_2b_1b_0)$ respectively, then the freshman's product of $a$ and $b$, denoted $a\boxtimes b$, is the integer $c$ with decimal representation $c=(... c_2c_1c_0)$ such that $c_i$ is the last digit of $a_i\cdot b_i$.

For example, $234 \boxtimes 765 = 480$.


Let $F(R,M)$ be the sum of $x_1 \boxtimes ... \boxtimes x_R$ for all sequences of integers $(x_1,...,x_R)$ with $0\leq x_i \leq M$.

For example, $F(2, 7) = 204$, and $F(23, 76) \equiv 5870548 \pmod{ 1\,000\,000\,009}$.


Find $F(234567,765432)$, give your answer modulo $1\,000\,000\,009$.


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
