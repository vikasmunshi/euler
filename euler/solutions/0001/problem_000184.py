#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 184
# https://projecteuler.net/problem=184
# Answer: 
# Notes: 
import textwrap
from typing import Any, Dict

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(**kwarg: Dict[str, Any]) -> SolutionResult:
    # enter the solution here
    raise NotImplementedError


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 184
https://projecteuler.net/problem=184
Consider the set $I_r$ of points $(x,y)$ with integer co-ordinates in the interior of the circle with radius $r$, centered at the origin, i.e. $x^2 + y^2 \lt r^2$.
For a radius of $2$, $I_2$ contains the nine points $(0,0)$, $(1,0)$, $(1,1)$, $(0,1)$, $(-1,1)$, $(-1,0)$, $(-1,-1)$, $(0,-1)$ and $(1,-1)$. There are eight triangles having all three vertices in $I_2$ which contain the origin in the interior. Two of them are shown below, the others are obtained from these by rotation.


For a radius of $3$, there are $360$ triangles containing the origin in the interior and having all vertices in $I_3$ and for $I_5$ the number is $10600$.

How many triangles are there containing the origin in the interior and having all three vertices in $I_{105}$?


''').strip()

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
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)