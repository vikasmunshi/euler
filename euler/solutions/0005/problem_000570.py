
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 570
# https://projecteuler.net/problem=570
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 570
    https://projecteuler.net/problem=570
    A snowflake of order $n$ is formed by overlaying an equilateral triangle (rotated by $180$ degrees) onto each equilateral triangle of the same size in a snowflake of order $n-1$. A snowflake of order $1$ is a single equilateral triangle.



  


Some areas of the snowflake are overlaid repeatedly. In the above picture, blue represents the areas that are one layer thick, red two layers thick, yellow three layers thick, and so on.

For an order $n$ snowflake, let $A(n)$ be the number of triangles that are one layer thick, and let $B(n)$ be the number of triangles that are three layers thick. Define $G(n) = \gcd(A(n), B(n))$.

E.g. $A(3) = 30$, $B(3) = 6$, $G(3)=6$.

$A(11) = 3027630$, $B(11) = 19862070$, $G(11) = 30$.

Further, $G(500) = 186$ and $\sum_{n=3}^{500}G(n)=5124$.

Find $\displaystyle \sum_{n=3}^{10^7}G(n)$.

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
