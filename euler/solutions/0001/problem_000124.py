
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 124
# https://projecteuler.net/problem=124
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 124
    https://projecteuler.net/problem=124
    The radical of $n$, $\operatorname{rad}(n)$, is the product of the distinct prime factors of $n$. For example, $504 = 2^3 \times 3^2 \times 7$, so $\operatorname{rad}(504) = 2 \times 3 \times 7 = 42$.
If we calculate $\operatorname{rad}(n)$ for $1 \le n \le 10$, then sort them on $\operatorname{rad}(n)$, and sorting on $n$ if the radical values are equal, we get:


   Unsorted
    
   Sorted


   n
   rad(n)
    
   n
   rad(n)
   k


   11
    
   111


   22
    
   222


   33
    
   423


   42
    
   824


   55
    
   335


   66
    
   936


   77
    
   557


   82
    
   668


   93
    
   779


   1010
    
   101010


Let $E(k)$ be the $k$-th element in the sorted $n$ column; for example, $E(4) = 8$ and $E(6) = 9$.
If $\operatorname{rad}(n)$ is sorted for $1 \le n \le 100000$, find $E(10000)$.

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
