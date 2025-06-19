#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 555
# https://projecteuler.net/problem=555
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
solution to Project Euler problem 555
https://projecteuler.net/problem=555

The McCarthy 91 function is defined as follows:
$$
M_{91}(n) = 
    \begin{cases}
        n - 10 & \text{if } n > 100 \\
        M_{91}(M_{91}(n+11)) & \text{if } 0 \leq n \leq 100
    \end{cases}
$$


We can generalize this definition by abstracting away the constants into new variables:

$$
M_{m,k,s}(n) = 
    \begin{cases}
        n - s & \text{if } n > m \\
        M_{m,k,s}(M_{m,k,s}(n+k)) & \text{if } 0 \leq n \leq m
    \end{cases}
$$


This way, we have $M_{91} = M_{100,11,10}$.


Let $F_{m,k,s}$ be the set of fixed points of $M_{m,k,s}$. That is, 

$$F_{m,k,s}= \left\{ n \in \mathbb{N} \, | \, M_{m,k,s}(n) = n \right\}$$


For example, the only fixed point of $M_{91}$ is $n = 91$. In other words, $F_{100,11,10}= \{91\}$.
 

Now, define $SF(m,k,s)$ as the sum of the elements in $F_{m,k,s}$ and let $S(p,m) = \displaystyle \sum_{1 \leq s < k \leq p}{SF(m,k,s)}$.


For example, $S(10, 10) = 225$ and $S(1000, 1000)=208724467$.


Find $S(10^6, 10^6)$.



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