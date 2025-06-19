
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 312
# https://projecteuler.net/problem=312
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 312
    https://projecteuler.net/problem=312
    - A Sierpiński graph of order-$1$ ($S_1$) is an equilateral triangle.

- $S_{n + 1}$ is obtained from $S_n$ by positioning three copies of $S_n$ so that every pair of copies has one common corner.




Let $C(n)$ be the number of cycles that pass exactly once through all the vertices of $S_n$.

For example, $C(3) = 8$ because eight such cycles can be drawn on $S_3$, as shown below:




It can also be verified that :

$C(1) = C(2) = 1$

$C(5) = 71328803586048$

$C(10\,000) \bmod 10^8 = 37652224$

$C(10\,000) \bmod 13^8 = 617720485$


Find $C(C(C(10\,000))) \bmod 13^8$.


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
