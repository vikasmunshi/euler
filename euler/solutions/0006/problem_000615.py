
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 615
# https://projecteuler.net/problem=615
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 615
    https://projecteuler.net/problem=615
    
Consider the natural numbers having at least $5$ prime factors, which don't have to be distinct.
 Sorting these numbers by size gives a list which starts with:

$32=2 \cdot 2 \cdot 2 \cdot 2 \cdot 2$
$48=2 \cdot 2 \cdot 2 \cdot 2 \cdot 3$
$64=2 \cdot 2 \cdot 2 \cdot 2 \cdot 2 \cdot 2$
$72=2 \cdot 2 \cdot 2 \cdot 3 \cdot 3$
$80=2 \cdot 2 \cdot 2 \cdot 2 \cdot 5$
$96=2 \cdot 2 \cdot 2 \cdot 2 \cdot 2 \cdot 3$
$\cdots$

So, for example, the fifth number with at least $5$ prime factors is $80$.


Find the millionth number with at least one million prime factors.
  Give your answer modulo $123454321$.


    """
    raise NotImplementedError


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
