#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 869
# https://projecteuler.net/problem=869
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
solution to Project Euler problem 869
https://projecteuler.net/problem=869

A prime is drawn uniformly from all primes not exceeding $N$. The prime is written in binary notation, and a player tries to guess it bit-by-bit starting at the least significant bit. The player scores one point for each bit they guess correctly. Immediately after each guess, the player is informed whether their guess was correct, and also whether it was the last bit in the number - in which case the game is over.


Let $E(N)$ be the expected number of points assuming that the player always guesses to maximize their score. For example, $E(10)=2$, achievable by always guessing "1". You are also given $E(30)=2.9$.


Find $E(10^8)$. Give your answer rounded to eight digits after the decimal point.

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