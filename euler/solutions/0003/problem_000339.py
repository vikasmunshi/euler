#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 339
# https://projecteuler.net/problem=339
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
solution to Project Euler problem 339
https://projecteuler.net/problem=339

"And he came towards a valley, through which ran a river; and the borders of the valley were wooded, and on each side of the river were level meadows. And on one side of the river he saw a flock of white sheep, and on the other a flock of black sheep. And whenever one of the white sheep bleated, one of the black sheep would cross over and become white; and when one of the black sheep bleated, one of the white sheep would cross over and become black."
en.wikisource.org



Initially each flock consists of $n$ sheep. Each sheep (regardless of colour) is equally likely to be the next sheep to bleat. After a sheep has bleated and a sheep from the other flock has crossed over, Peredur may remove a number of white sheep in order to maximize the expected final number of black sheep. Let $E(n)$ be the expected final number of black sheep if Peredur uses an optimal strategy.



You are given that $E(5) = 6.871346$ rounded to $6$ places behind the decimal point.

Find $E(10\,000)$ and give your answer rounded to $6$ places behind the decimal point.




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