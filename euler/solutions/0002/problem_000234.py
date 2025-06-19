#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 234
# https://projecteuler.net/problem=234
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
solution to Project Euler problem 234
https://projecteuler.net/problem=234
For an integer $n \ge 4$, we define the lower prime square root of $n$, denoted by $\operatorname{lps}(n)$, as the largest prime $\le \sqrt n$ and the upper prime square root of $n$, $\operatorname{ups}(n)$, as the smallest prime $\ge \sqrt n$.
So, for example, $\operatorname{lps}(4) = 2 = \operatorname{ups}(4)$, $\operatorname{lps}(1000) = 31$, $\operatorname{ups}(1000) = 37$.

Let us call an integer $n \ge 4$ semidivisible, if one of $\operatorname{lps}(n)$ and $\operatorname{ups}(n)$ divides $n$, but not both.

The sum of the semidivisible numbers not exceeding $15$ is $30$, the numbers are $8$, $10$ and $12$.
 $15$ is not semidivisible because it is a multiple of both $\operatorname{lps}(15) = 3$ and $\operatorname{ups}(15) = 5$.

As a further example, the sum of the $92$ semidivisible numbers up to $1000$ is $34825$.

What is the sum of all semidivisible numbers not exceeding $999966663333$?

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