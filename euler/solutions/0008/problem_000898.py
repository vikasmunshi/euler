#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 898
# https://projecteuler.net/problem=898
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
solution to Project Euler problem 898
https://projecteuler.net/problem=898

Claire Voyant is a teacher playing a game with a class of students.
A fair coin is tossed on the table. All the students can see the outcome of the toss, but Claire cannot.
Each student then tells Claire whether the outcome is head or tail. The students may lie, but Claire knows the probability that each individual student lies. Moreover, the students lie independently.
After that, Claire attempts to guess the outcome using an optimal strategy.


For example, for a class of four students with lying probabilities $20\%,40\%,60\%,80\%$, Claire guesses correctly with probability 0.832.


Find the probability that Claire guesses correctly for a class of 51 students each lying with a probability of $25\%, 26\%, ..., 75\%$
 respectively.


Give your answer rounded to 10 digits after the decimal point.


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