#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 791
# https://projecteuler.net/problem=791
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
solution to Project Euler problem 791
https://projecteuler.net/problem=791
Denote the average of $k$ numbers $x_1, ..., x_k$ by $\bar{x} = \frac{1}{k} \sum_i x_i$. Their variance is defined as $\frac{1}{k} \sum_i \left( x_i - \bar{x} \right) ^ 2$.

Let $S(n)$ be the sum of all quadruples of integers $(a,b,c,d)$ satisfying $1 \leq a \leq b \leq c \leq d \leq n$ such that their average is exactly twice their variance.

For $n=5$, there are $5$ such quadruples, namely: $(1, 1, 1, 3), (1, 1, 3, 3), (1, 2, 3, 4), (1, 3, 4, 4), (2, 2, 3, 5)$.

Hence $S(5)=48$. You are also given $S(10^3)=37048340$.

Find $S(10^8)$. Give your answer modulo $433494437$.

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