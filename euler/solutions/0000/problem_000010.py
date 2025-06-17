#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 10
# https://projecteuler.net/problem=10
# Answer: answers={10: 17, 2000000: 142913828922}
# Notes: 
import textwrap

from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_num': 10},
        answer=17,
    ),
    ProblemArgs(
        kwargs={'max_num': 2000000},
        answer=142913828922,
    ),
]


def solution(*, max_num: int) -> int:
    return sum(gen_primes_sundaram_sieve(max_limit=max_num))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 10
https://projecteuler.net/problem=10
The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.
Find the sum of all the primes below two million.
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
