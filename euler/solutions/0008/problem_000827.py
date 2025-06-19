
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 827
# https://projecteuler.net/problem=827
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 827
    https://projecteuler.net/problem=827
    
Define $Q(n)$ to be the smallest number that occurs in exactly $n$ Pythagorean triples $(a,b,c)$ where $a \lt b \lt c$.


For example, $15$ is the smallest number occurring in exactly $5$ Pythagorean triples:
$$(9,12,\mathbf{15})\quad (8,\mathbf{15},17)\quad (\mathbf{15},20,25)\quad (\mathbf{15},36,39)\quad (\mathbf{15},112,113)$$
and so $Q(5) = 15$.


You are also given $Q(10)=48$ and $Q(10^3)=8064000$.


Find $\displaystyle \sum_{k=1}^{18} Q(10^k)$. Give your answer modulo $409120391$.



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
