
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 906
# https://projecteuler.net/problem=906
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 906
    https://projecteuler.net/problem=906
    
Three friends attempt to collectively choose one of $n$ options, labeled $1,...,n$, based upon their individual preferences. They choose option $i$ if for every alternative option $j$ at least two of the three friends prefer $i$ over $j$. If no such option $i$ exists they fail to reach an agreement.


Define $P(n)$ to be the probability the three friends successfully reach an agreement and choose one option, where each of the friends' individual order of preference is given by a (possibly different) random permutation of $1,...,n$.


You are given $P(3)=17/18$ and $P(10)\approx0.6760292265$.


Find $P(20\,000)$. Give your answer rounded to ten places after the decimal point.


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
