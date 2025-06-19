#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 527
# https://projecteuler.net/problem=527
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
solution to Project Euler problem 527
https://projecteuler.net/problem=527
A secret integer $t$ is selected at random within the range $1 \le t \le n$. 

The goal is to guess the value of $t$ by making repeated guesses, via integer $g$. After a guess is made, there are three possible outcomes, in which it will be revealed that either $g \lt t$, $g = t$, or $g \gt t$. Then the process can repeat as necessary.

Normally, the number of guesses required on average can be minimized with a binary search: Given a lower bound $L$ and upper bound $H$ (initialized to $L = 1$ and $H = n$), let $g = \lfloor(L+H)/2\rfloor$ where $\lfloor \cdot \rfloor$ is the integer floor function. If $g = t$, the process ends. Otherwise, if $g \lt t$, set $L = g+1$, but if $g \gt t$ instead, set $H = g - 1$. After setting the new bounds, the search process repeats, and ultimately ends once $t$ is found. Even if $t$ can be deduced without searching, assume that a search will be required anyway to confirm the value.

Your friend Bob believes that the standard binary search is not that much better than his randomized variant: Instead of setting $g = \lfloor(L+H)/2\rfloor$, simply let $g$ be a random integer between $L$ and $H$, inclusive. The rest of the algorithm is the same as the standard binary search. This new search routine will be referred to as a random binary search.

Given that $1 \le t \le n$ for random $t$, let $B(n)$ be the expected number of guesses needed to find $t$ using the standard binary search, and let $R(n)$ be the expected number of guesses needed to find $t$ using the random binary search. For example, $B(6) = 2.33333333$ and $R(6) = 2.71666667$ when rounded to $8$ decimal places.

Find $R(10^{10}) - B(10^{10})$ rounded to $8$ decimal places.

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