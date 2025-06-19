#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 576
# https://projecteuler.net/problem=576
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
solution to Project Euler problem 576
https://projecteuler.net/problem=576

A bouncing point moves counterclockwise along a circle with circumference $1$ with jumps of constant length $l \lt 1$, until it hits a gap of length $g \lt 1$, that is placed in a distance $d$ counterclockwise from the starting point. The gap does not include the starting point, that is $g+d \lt 1$.

Let $S(l,g,d)$ be the sum of the length of all jumps, until the point falls into the gap. It can be shown that $S(l,g,d)$ is finite for any irrational jump size $l$, regardless of the values of $g$ and $d$.

Examples: 

$S(\sqrt{\frac 1 2}, 0.06, 0.7)=0.7071 \cdots$, $S(\sqrt{\frac 1 2}, 0.06, 0.3543)=1.4142 \cdots$ and 
 $S(\sqrt{\frac 1 2}, 0.06, 0.2427)=16.2634 \cdots$.

Let $M(n, g)$ be the maximum of $ \sum S(\sqrt{\frac 1 p}, g, d)$ for all primes $p \le n$ and any valid value of $d$.

Examples:

$M(3, 0.06) =29.5425 \cdots$, since $S(\sqrt{\frac 1 2}, 0.06, 0.2427)+S(\sqrt{\frac 1 3}, 0.06, 0.2427)=29.5425 \cdots$ is the maximal reachable sum for $g=0.06$. 

$M(10, 0.01)=266.9010 \cdots$ 

Find $M(100, 0.00002)$, rounded to $4$ decimal places.

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