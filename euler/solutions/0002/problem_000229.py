#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 229
# https://projecteuler.net/problem=229
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
solution to Project Euler problem 229
https://projecteuler.net/problem=229
Consider the number $3600$. It is very special, because
\begin{alignat}{2}
3600 &= 48^2 + &&36^2\\
3600 &= 20^2 + 2 \times &&40^2\\
3600 &= 30^2 + 3 \times &&30^2\\
3600 &= 45^2 + 7 \times &&15^2
\end{alignat}

Similarly, we find that $88201 = 99^2 + 280^2 = 287^2 + 2 \times 54^2 = 283^2 + 3 \times 52^2 = 197^2 + 7 \times 84^2$.

In 1747, Euler proved which numbers are representable as a sum of two squares.
We are interested in the numbers $n$ which admit representations of all of the following four types:
\begin{alignat}{2}
n &= a_1^2 + && b_1^2\\
n &= a_2^2 + 2 && b_2^2\\
n &= a_3^2 + 3 && b_3^2\\
n &= a_7^2 + 7 && b_7^2,
\end{alignat}
where the $a_k$ and $b_k$ are positive integers.

There are $75373$ such numbers that do not exceed $10^7$.


How many such numbers are there that do not exceed $2 \times 10^9$?

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