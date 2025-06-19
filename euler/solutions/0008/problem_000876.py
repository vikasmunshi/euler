
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 876
# https://projecteuler.net/problem=876
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 876
    https://projecteuler.net/problem=876
    
Starting with three numbers $a, b, c$, at each step do one of the three operations:

change $a$ to $2(b + c) - a$;
change $b$ to $2(c + a) - b$;
change $c$ to $2(a + b) - c$;



Define $f(a, b, c)$ to be the minimum number of steps required for one number to become zero. If this is not possible then $f(a, b, c)=0$.


For example, $f(6,10,35)=3$:
$$(6,10,35) \to (6,10,-3) \to (8,10,-3) \to (8,0,-3).$$
However, $f(6,10,36)=0$ as no series of operations leads to a zero number.


Also define $F(a, b)=\sum_{c=1}^\infty f(a,b,c)$.
You are given $F(6,10)=17$ and $F(36,100)=179$.


Find $\displaystyle\sum_{k=1}^{18}F(6^k,10^k)$.


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
