#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 771
# https://projecteuler.net/problem=771
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
solution to Project Euler problem 771
https://projecteuler.net/problem=771

We define a pseudo-geometric sequence to be a finite sequence $a_0, a_1, ...c, a_n$ of positive integers, satisfying the following conditions:

$n \geq 4$, i.e. the sequence has at least $5$ terms.
$0 \lt a_0 \lt a_1 \lt \cdots \lt a_n$, i.e. the sequence is strictly increasing.
$| a_i^2 - a_{i - 1}a_{i + 1} | \le 2$ for $1 \le i \le n-1$.


Let $G(N)$ be the number of different pseudo-geometric sequences whose terms do not exceed $N$.

For example, $G(6) = 4$, as the following $4$ sequences give a complete list:
$1, 2, 3, 4, 5 \qquad 1, 2, 3, 4, 6 \qquad 2, 3, 4, 5, 6 \qquad 1, 2, 3, 4, 5, 6$ 

Also, $G(10) = 26$, $G(100) = 4710$ and $G(1000) = 496805$.

Find $G(10^{18})$. Give your answer modulo $1\,000\,000\,007$.

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