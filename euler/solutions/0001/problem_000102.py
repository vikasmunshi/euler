
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 102
# https://projecteuler.net/problem=102
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 102
    https://projecteuler.net/problem=102
    Three distinct points are plotted at random on a Cartesian plane, for which $-1000 \le x, y \le 1000$, such that a triangle is formed.
Consider the following two triangles:
\begin{gather}
A(-340,495), B(-153,-910), C(835,-947)\\
X(-175,41), Y(-421,-714), Z(574,-645)
\end{gather}
It can be verified that triangle $ABC$ contains the origin, whereas triangle $XYZ$ does not.
Using triangles.txt (right click and 'Save Link/Target As...'), a 27K text file containing the co-ordinates of one thousand "random" triangles, find the number of triangles for which the interior contains the origin.
NOTE: The first two examples in the file represent the triangles in the example given above.


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
