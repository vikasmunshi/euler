#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 561
# https://projecteuler.net/problem=561
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
solution to Project Euler problem 561
https://projecteuler.net/problem=561

Let $S(n)$ be the number of pairs $(a,b)$ of distinct divisors of $n$ such that $a$ divides $b$.

For $n=6$ we get the following pairs: $(1,2), (1,3), (1,6),( 2,6)$ and $(3,6)$. So $S(6)=5$.

Let $p_m\#$ be the product of the first $m$ prime numbers,  so $p_2\# = 2*3 = 6$.

Let $E(m, n)$ be the highest integer $k$ such that $2^k$ divides $S((p_m\#)^n)$.

$E(2,1) = 0$ since $2^0$ is the highest power of 2 that divides S(6)=5.

Let $Q(n)=\sum_{i=1}^{n} E(904961, i)$

$Q(8)=2714886$.


Evaluate $Q(10^{12})$. 


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