#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 508
# https://projecteuler.net/problem=508
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
solution to Project Euler problem 508
https://projecteuler.net/problem=508
Consider the Gaussian integer $i-1$. A base $i-1$ representation of a Gaussian integer $a+bi$ is a finite sequence of digits $d_{n - 1}d_{n - 2}\cdots d_1 d_0$ such that:

$a+bi = d_{n - 1}(i - 1)^{n - 1} + d_{n - 2}(i - 1)^{n - 2} + \cdots + d_1(i - 1) + d_0$
Each $d_k$ is in $\{0,1\}$
There are no leading zeroes, i.e. $d_{n-1} \ne 0$, unless $a+bi$ is itself $0$
Here are base $i-1$ representations of a few Gaussian integers:


$11+24i \to 111010110001101$

$24-11i \to 110010110011$

$8+0i \to 111000000$

$-5+0i \to 11001101$

$0+0i \to 0$


Remarkably, every Gaussian integer has a unique base $i-1$ representation!


Define $f(a + bi)$ as the number of $1$s in the unique base $i-1$ representation of $a + bi$. For example, $f(11+24i) = 9$ and $f(24-11i) = 7$.


Define $B(L)$ as the sum of $f(a + bi)$ for all integers $a, b$ such that $|a| \le L$ and $|b| \le L$. For example, $B(500) = 10795060$.


Find $B(10^{15}) \bmod 1\,000\,000\,007$.

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