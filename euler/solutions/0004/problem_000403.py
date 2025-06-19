#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 403
# https://projecteuler.net/problem=403
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
solution to Project Euler problem 403
https://projecteuler.net/problem=403

For integers $a$ and $b$, we define $D(a, b)$ as the domain enclosed by the parabola $y = x^2$ and the line $y = a\cdot x + b$:
$D(a, b) = \{(x, y) \mid x^2 \leq y \leq a\cdot x + b \}$.


$L(a, b)$ is defined as the number of lattice points contained in $D(a, b)$.

For example, $L(1, 2) = 8$ and $L(2, -1) = 1$.


We also define $S(N)$ as the sum of $L(a, b)$ for all the pairs $(a, b)$ such that the area of $D(a, b)$ is a rational number and $|a|,|b| \leq N$.

We can verify that $S(5) = 344$ and $S(100) = 26709528$.


Find $S(10^{12})$. Give your answer mod $10^8$.


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