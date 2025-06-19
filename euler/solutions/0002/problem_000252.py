#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 252
# https://projecteuler.net/problem=252
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
solution to Project Euler problem 252
https://projecteuler.net/problem=252

Given a set of points on a plane, we define a convex hole to be a convex polygon having as vertices any of the given points and not containing any of the given points in its interior (in addition to the vertices, other given points may lie on the perimeter of the polygon). 


As an example, the image below shows a set of twenty points and a few such convex holes. 
The convex hole shown as a red heptagon has an area equal to $1049694.5$ square units, which is the highest possible area for a convex hole on the given set of points.




For our example, we used the first $20$ points $(T_{2k - 1}, T_{2k})$, for $k = 1,2,...,20$, produced with the pseudo-random number generator:

\begin{align}
S_0 &= 290797\\
S_{n + 1} &= S_n^2 \bmod 50515093\\
T_n &= (S_n \bmod 2000) - 1000
\end{align}


i.e. $(527, 144), (-488, 732), (-454, -947), ...$


What is the maximum area for a convex hole on the set containing the first $500$ points in the pseudo-random sequence?
 Specify your answer including one digit after the decimal point.







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