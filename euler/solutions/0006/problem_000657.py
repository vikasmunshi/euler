#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 657
# https://projecteuler.net/problem=657
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
solution to Project Euler problem 657
https://projecteuler.net/problem=657
In the context of formal languages, any finite sequence of letters of a given alphabet $\Sigma$ is called a word over $\Sigma$. We call a word incomplete if it does not contain every letter of $\Sigma$.

For example, using the alphabet $\Sigma=\{ a, b, c\}$, '$ab$', '$abab$' and '$\,$' (the empty word) are incomplete words over $\Sigma$, while '$abac$' is a complete word over $\Sigma$.

Given an alphabet $\Sigma$ of $\alpha$ letters, we define $I(\alpha,n)$ to be the number of incomplete words over $\Sigma$ with a length not exceeding $n$. 

For example, $I(3,0)=1$, $I(3,2)=13$ and $I(3,4)=79$.

Find $I(10^7,10^{12})$. Give your answer modulo $1\,000\,000\,007$.

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