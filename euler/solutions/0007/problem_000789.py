#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 789
# https://projecteuler.net/problem=789
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
solution to Project Euler problem 789
https://projecteuler.net/problem=789
Given an odd prime $p$, put the numbers $1,...,p-1$ into $\frac{p-1}{2}$ pairs such that each number appears exactly once. Each pair $(a,b)$ has a cost of $ab \bmod p$. For example, if $p=5$ the pair $(3,4)$ has a cost of $12 \bmod 5 = 2$.

The total cost of a pairing is the sum of the costs of its pairs. We say that such pairing is optimal if its total cost is minimal for that $p$.

For example, if $p = 5$, then there is a unique optimal pairing: $(1, 2), (3, 4)$, with total cost of $2 + 2 = 4$.

The cost product of a pairing is the product of the costs of its pairs. For example, the cost product of the optimal pairing for $p = 5$ is $2 \cdot 2 = 4$.

It turns out that all optimal pairings for $p = 2\,000\,000\,011$ have the same cost product.

Find the value of this product.

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