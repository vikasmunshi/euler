#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 338
# https://projecteuler.net/problem=338
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
solution to Project Euler problem 338
https://projecteuler.net/problem=338
A rectangular sheet of grid paper with integer dimensions $w \times h$ is given. Its grid spacing is $1$.

When we cut the sheet along the grid lines into two pieces and rearrange those pieces without overlap, we can make new rectangles with different dimensions.
For example, from a sheet with dimensions $9 \times 4$, we can make rectangles with dimensions $18 \times 2$, $12 \times 3$ and $6 \times 6$ by cutting and rearranging as below:





Similarly, from a sheet with dimensions $9 \times 8$, we can make rectangles with dimensions $18 \times 4$ and $12 \times 6$.

For a pair $w$ and $h$, let $F(w, h)$ be the number of distinct rectangles that can be made from a sheet with dimensions $w \times h$.

For example, $F(2,1) = 0$, $F(2,2) = 1$, $F(9,4) = 3$ and $F(9,8) = 2$. 

Note that rectangles congruent to the initial one are not counted in $F(w, h)$.

Note also that rectangles with dimensions $w \times h$ and dimensions $h \times w$ are not considered distinct.

For an integer $N$, let $G(N)$ be the sum of $F(w, h)$ for all pairs $w$ and $h$ which satisfy $0 \lt h \le w \le N$.

We can verify that $G(10) = 55$, $G(10^3) = 971745$ and $G(10^5) = 9992617687$.

Find $G(10^{12})$. Give your answer modulo $10^8$.

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