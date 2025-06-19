
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 580
# https://projecteuler.net/problem=580
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 580
    https://projecteuler.net/problem=580
    
A Hilbert number is any positive integer of the form $4k+1$ for integer $k\geq 0$.  We shall define a squarefree Hilbert number as a Hilbert number which is not divisible by the square of any Hilbert number other than one.  For example, $117$ is a squarefree Hilbert number, equaling $9\times13$.  However $6237$ is a Hilbert number that is not squarefree in this sense, as it is divisible by $9^2$.  The number $3969$ is also not squarefree, as it is divisible by both $9^2$ and $21^2$.  


There are $2327192$ squarefree Hilbert numbers below $10^7$. 

How many squarefree Hilbert numbers are there below $10^{16}$?


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
