
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 347
# https://projecteuler.net/problem=347
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 347
    https://projecteuler.net/problem=347
    
The largest integer $\le 100$ that is only divisible by both the primes $2$ and $3$ is $96$, as $96=32\times 3=2^5 \times 3$.
For two distinct primes $p$ and $q$ let $M(p,q,N)$ be the largest positive integer $\le N$ only divisible by both $p$ and $q$ and $M(p,q,N)=0$ if such a positive integer does not exist.


E.g. $M(2,3,100)=96$.
 
$M(3,5,100)=75$ and not $90$ because $90$ is divisible by $2$, $3$ and $5$.

Also $M(2,73,100)=0$ because there does not exist a positive integer $\le 100$ that is divisible by both $2$ and $73$.


Let $S(N)$ be the sum of all distinct $M(p,q,N)$.
$S(100)=2262$.


Find $S(10\,000\,000)$.







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
