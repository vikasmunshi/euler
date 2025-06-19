#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 719
# https://projecteuler.net/problem=719
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
solution to Project Euler problem 719
https://projecteuler.net/problem=719

We define an $S$-number to be a natural number, $n$, that is a perfect square and its square root can be obtained by splitting the decimal representation of $n$ into $2$ or more numbers then adding the numbers.


For example, $81$ is an $S$-number because $\sqrt{81} = 8+1$.

$6724$ is an $S$-number: $\sqrt{6724} = 6+72+4$. 

$8281$ is an $S$-number: $\sqrt{8281} = 8+2+81 = 82+8+1$.

$9801$ is an $S$-number: $\sqrt{9801}=98+0+1$.


Further we define $T(N)$ to be the sum of all $S$ numbers $n\le N$. You are given $T(10^4) = 41333$.


Find $T(10^{12})$.


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