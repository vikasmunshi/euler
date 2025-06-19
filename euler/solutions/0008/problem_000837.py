#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 837
# https://projecteuler.net/problem=837
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
solution to Project Euler problem 837
https://projecteuler.net/problem=837

Amidakuji (Japanese: 阿弥陀籤) is a method for producing a random permutation of a set of objects.


In the beginning, a number of parallel vertical lines are drawn, one for each object. Then a specified number of horizontal rungs are added, each lower than any previous rungs. Each rung is drawn as a line segment spanning a randomly select pair of adjacent vertical lines.


For example, the following diagram depicts an Amidakuji with three objects ($A$, $B$, $C$) and six rungs:





The coloured lines in the diagram illustrate how to form the permutation. For each object, starting from the top of its vertical line, trace downwards but follow any rung encountered along the way, and record which vertical we end up on. In this example, the resulting permutation happens to be the identity: $A\mapsto A$, $B\mapsto B$, $C\mapsto C$.


Let $a(m, n)$ be the number of different three-object Amidakujis that have $m$ rungs between $A$ and $B$, and $n$ rungs between $B$ and $C$, and whose outcome is the identity permutation. For example, $a(3, 3) = 2$, because the Amidakuji shown above and its mirror image are the only ones with the required property.


You are also given that $a(123, 321) \equiv 172633303 \pmod{1234567891}$.


Find $a(123456789, 987654321)$. Give your answer modulo $1234567891$.

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