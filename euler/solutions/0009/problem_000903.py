#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 903
# https://projecteuler.net/problem=903
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
solution to Project Euler problem 903
https://projecteuler.net/problem=903
A permutation $\pi$ of $\{1, ..., n\}$ can be represented in one-line notation as $\pi(1),\ldots,\pi(n) $. If all $n!$ permutations are written in lexicographic order then $\textrm{rank}(\pi)$ is the position of $\pi$ in this 1-based list.

For example, $\text{rank}(2,1,3) = 3$ because the six permutations of $\{1, 2, 3\}$ in lexicographic order are:
$$1, 2, 3\quad 1, 3, 2 \quad 2, 1, 3 \quad 2, 3, 1 \quad 3, 1, 2 \quad 3, 2, 1$$


Let $Q(n)$ be the sum $\sum_{\pi}\sum_{i = 1}^{n!} \text{rank}(\pi^i)$, where $\pi$ ranges over all permutations of $\{1, ..., n\}$, and $\pi^i$ is the permutation arising from applying $\pi$ $i$ times.

For example, $Q(2) = 5$, $Q(3) = 88$, $Q(6) = 133103808$ and $Q(10) \equiv 468421536 \pmod {10^9 + 7}$.

Find $Q(10^6)$. Give your answer modulo  $(10^9 + 7)$.


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