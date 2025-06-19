#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 387
# https://projecteuler.net/problem=387
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
solution to Project Euler problem 387
https://projecteuler.net/problem=387
A Harshad or Niven number is a number that is divisible by the sum of its digits.

$201$ is a Harshad number because it is divisible by $3$ (the sum of its digits.)

When we truncate the last digit from $201$, we get $20$, which is a Harshad number.

When we truncate the last digit from $20$, we get $2$, which is also a Harshad number.

Let's call a Harshad number that, while recursively truncating the last digit, always results in a Harshad number a right truncatable Harshad number.  

Also:

$201/3=67$ which is prime.

Let's call a Harshad number that, when divided by the sum of its digits, results in a prime a strong Harshad number.

Now take the number $2011$ which is prime.

When we truncate the last digit from it we get $201$, a strong Harshad number that is also right truncatable.

Let's call such primes strong, right truncatable Harshad primes.

You are given that the sum of the strong, right truncatable Harshad primes less than $10000$ is $90619$.

Find the sum of the strong, right truncatable Harshad primes less than $10^{14}$.

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