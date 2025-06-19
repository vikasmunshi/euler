
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 659
# https://projecteuler.net/problem=659
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 659
    https://projecteuler.net/problem=659
    
Consider the sequence  $n^2+3$ with $n \ge 1$. 
 
If we write down the first terms of this sequence we get:

$4, 7, 12, 19, 28, 39, 52, 67, 84, 103, 124, 147, 172, 199, 228, 259, 292, 327, 364, ...$ .

We see that the terms for $n=6$ and $n=7$ ($39$ and $52$) are both divisible by $13$.

In fact $13$ is the largest prime dividing any two successive terms of this sequence.


Let $P(k)$ be the largest prime  that divides any two successive terms of the sequence $n^2+k^2$.


Find the last $18$ digits of $\displaystyle \sum_{k=1}^{10\,000\,000} P(k)$.




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
