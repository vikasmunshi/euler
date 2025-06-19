
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 587
# https://projecteuler.net/problem=587
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 587
    https://projecteuler.net/problem=587
    
A square is drawn around a circle as shown in the diagram below on the left.

We shall call the blue shaded region the L-section.

A line is drawn from the bottom left of the square to the top right as shown in the diagram on the right.

We shall call the orange shaded region a concave triangle.





It should be clear that the concave triangle occupies exactly half of the L-section.



Two circles are placed next to each other horizontally, a rectangle is drawn around both circles, and a line is drawn from the bottom left to the top right as shown in the diagram below.





This time the concave triangle occupies approximately 36.46% of the L-section.


If $n$ circles are placed next to each other horizontally, a rectangle is drawn around the n circles, and a line is drawn from the bottom left to the top right, then it can be shown that the least value of n for which the concave triangle occupies less than 10% of the L-section is $n = 15$.


What is the least value of $n$ for which the concave triangle occupies less than 0.1% of the L-section?



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
