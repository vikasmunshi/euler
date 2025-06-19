#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 394
# https://projecteuler.net/problem=394
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
solution to Project Euler problem 394
https://projecteuler.net/problem=394

Jeff eats a pie in an unusual way.

The pie is circular. He starts with slicing an initial cut in the pie along a radius.

While there is at least a given fraction $F$ of pie left, he performs the following procedure:

- He makes two slices from the pie centre to any point of what is remaining of the pie border, any point on the remaining pie border equally likely. This will divide the remaining pie into three pieces.
 
- Going counterclockwise from the initial cut, he takes the first two pie pieces and eats them.

When less than a fraction $F$ of pie remains, he does not repeat this procedure. Instead, he eats all of the remaining pie.






For $x \ge 1$, let $E(x)$ be the expected number of times Jeff repeats the procedure above with $F = 1/x$.

It can be verified that $E(1) = 1$, $E(2) \approx 1.2676536759$, and $E(7.5) \approx 2.1215732071$.


Find $E(40)$ rounded to $10$ decimal places behind the decimal point.




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