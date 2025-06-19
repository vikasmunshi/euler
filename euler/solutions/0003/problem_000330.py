#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 330
# https://projecteuler.net/problem=330
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
solution to Project Euler problem 330
https://projecteuler.net/problem=330
An infinite sequence of real numbers $a(n)$ is defined for all integers $n$ as follows:
$$a(n) = \begin{cases}
1 & n \lt 0\\
\sum \limits_{i = 1}^{\infty}{\dfrac{a(n - i)}{i!}} & n \ge 0
\end{cases}$$

For example,


$a(0) = \dfrac{1}{1!} + \dfrac{1}{2!} + \dfrac{1}{3!} + \cdots = e - 1$

$a(1) = \dfrac{e - 1}{1!} + \dfrac{1}{2!} + \dfrac{1}{3!} + \cdots = 2e - 3$

$a(2) = \dfrac{2e - 3}{1!} + \dfrac{e - 1}{2!} + \dfrac{1}{3!} + \cdots = \dfrac{7}{2}e - 6$

with $e = 2.7182818...$ being Euler's constant.

It can be shown that $a(n)$ is of the form $\dfrac{A(n)e + B(n)}{n!}$ for integers $A(n)$ and $B(n)$.

For example, $a(10) = \dfrac{328161643e - 652694486}{10!}$.

Find $A(10^9) + B(10^9)$ and give your answer mod $77\,777\,777$.

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