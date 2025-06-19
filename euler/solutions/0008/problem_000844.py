#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 844
# https://projecteuler.net/problem=844
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
solution to Project Euler problem 844
https://projecteuler.net/problem=844
Consider positive integer solutions to
$a^2+b^2+c^2 = 3abc$
For example, $(1,5,13)$ is a solution. We define a 3-Markov number to be any part of a solution, so $1$, $5$ and $13$ are all 3-Markov numbers. Adding distinct 3-Markov numbers $\le 10^3$ would give $2797$.

Now we define a $k$-Markov number to be a positive integer that is part of a solution to:
$\displaystyle \sum_{i=1}^{k}x_i^2=k\prod_{i=1}^{k}x_i,\quad x_i\text{ are positive integers}$

Let $M_k(N)$ be the sum of $k$-Markov numbers $\le N$. Hence $M_3(10^{3})=2797$, also $M_8(10^8) = 131493335$.

Define $\displaystyle S(K,N)=\sum_{k=3}^{K}M_k(N)$. You are given $S(4, 10^2)=229$ and $S(10, 10^8)=2383369980$.

Find $S(10^{18}, 10^{18})$. Give your answer modulo $1\,405\,695\,061$.

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