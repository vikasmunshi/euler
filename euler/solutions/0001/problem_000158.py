#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 158
# https://projecteuler.net/problem=158
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
solution to Project Euler problem 158
https://projecteuler.net/problem=158
Taking three different letters from the $26$ letters of the alphabet, character strings of length three can be formed.

Examples are 'abc', 'hat' and 'zyx'.

When we study these three examples we see that for 'abc' two characters come lexicographically after its neighbour to the left.
 
For 'hat' there is exactly one character that comes lexicographically after its neighbour to the left. For 'zyx' there are zero characters that come lexicographically after its neighbour to the left.

In all there are $10400$ strings of length $3$ for which exactly one character comes lexicographically after its neighbour to the left.
We now consider strings of $n \le 26$ different characters from the alphabet.
 
For every $n$, $p(n)$ is the number of strings of length $n$ for which exactly one character comes lexicographically after its neighbour to the left. 
What is the maximum value of $p(n)$?

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