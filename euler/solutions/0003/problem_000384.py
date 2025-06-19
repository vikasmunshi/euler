#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 384
# https://projecteuler.net/problem=384
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
solution to Project Euler problem 384
https://projecteuler.net/problem=384
Define the sequence $a(n)$ as the number of adjacent pairs of ones in the binary expansion of $n$ (possibly overlapping).

E.g.: $a(5) = a(101_2) = 0$, $a(6) = a(110_2) = 1$, $a(7) = a(111_2) = 2$.

Define the sequence $b(n) = (-1)^{a(n)}$.

This sequence is called the Rudin-Shapiro sequence.
Also consider the summatory sequence of $b(n)$: $s(n) = \sum \limits_{i = 0}^n b(i)$.

The first couple of values of these sequences are:

$n$
$0$
$1$
$2$
$3$
$4$
$5$
$6$
$7$

$a(n)$
$0$
$0$
$0$
$1$
$0$
$0$
$1$
$2$

$b(n)$
$1$
$1$
$1$
$-1$
$1$
$1$
$-1$
$1$

$s(n)$
$1$
$2$
$3$
$2$
$3$
$4$
$3$
$4$


The sequence $s(n)$ has the remarkable property that all elements are positive and every positive integer $k$ occurs exactly $k$ times.

Define $g(t,c)$, with $1 \le c \le t$, as the index in $s(n)$ for which $t$ occurs for the $c$'th time in $s(n)$.

E.g.: $g(3,3) = 6$, $g(4,2) = 7$ and $g(54321,12345) = 1220847710$.

Let $F(n)$ be the Fibonacci sequence defined by:

$F(0)=F(1)=1$ and

$F(n)=F(n-1)+F(n-2)$ for $n \gt 1$.

Define $GF(t)=g(F(t),F(t-1))$.

Find $\sum GF(t)$ for $2 \le t \le 45$.

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