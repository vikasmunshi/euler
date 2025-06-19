#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 693
# https://projecteuler.net/problem=693
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
solution to Project Euler problem 693
https://projecteuler.net/problem=693
Two positive integers $x$ and $y$ ($x > y$) can generate a sequence in the following manner:

$a_x = y$ is the first term,
$a_{z+1} = a_z^2 \bmod z$ for $z = x, x+1,x+2,\ldots$ and
the generation stops when a term becomes $0$ or $1$.

The number of terms in this sequence is denoted $l(x,y)$.

For example, with $x = 5$ and $y = 3$, we get $a_5 = 3$, $a_6 = 3^2 \bmod 5 = 4$, $a_7 = 4^2\bmod 6 = 4$, etc. Giving the sequence of 29 terms:

$	3,4,4,2,4,7,9,4,4,3,9,6,4,16,4,16,16,4,16,3,9,6,10,19,25,16,16,8,0		$

Hence $l(5,3) = 29$.

$g(x)$ is defined  to be the maximum value of $l(x,y)$ for $y \lt x$. For example, $g(5) = 29$.

Further, define $f(n)$ to be the maximum value of $g(x)$ for $x \le n$. For example, $f(100) = 145$ and $f(10\,000) = 8824$.

Find $f(3\,000\,000)$.

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