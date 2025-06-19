#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 744
# https://projecteuler.net/problem=744
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
solution to Project Euler problem 744
https://projecteuler.net/problem=744
"What? Where? When?" is a TV game show in which a team of experts attempt to answer questions. The following is a simplified version of the game.

It begins with $2n+1$ envelopes. $2n$ of them contain a question and one contains a RED card.

In each round one of the remaining envelopes is randomly chosen. If the envelope contains the RED card the game ends. If the envelope contains a question the expert gives their answer. If their answer is correct they earn one point, otherwise the viewers earn one point. The game ends normally when either the expert obtains n points or the viewers obtain n points.

Assuming that the expert provides the correct answer with a fixed probability $p$, let $f(n,p)$ be the probability that the game ends normally (i.e. RED card never turns up).

You are given (rounded to 10 decimal places) that

$f(6,\frac{1}{2})=0.2851562500$,

$f(10,\frac{3}{7})=0.2330040743$,

$f(10^4,0.3)=0.2857499982$.


Find $f(10^{11},0.4999)$. Give your answer rounded to 10 places behind the decimal point.

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