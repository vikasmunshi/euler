#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 282
# https://projecteuler.net/problem=282
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
solution to Project Euler problem 282
https://projecteuler.net/problem=282
$\def\htmltext#1{\style{font-family:inherit;}{\text{#1}}}$

For non-negative integers $m$, $n$, the Ackermann function $A(m,n)$ is defined as follows:

$$
A(m,n) = \cases{
n+1 &$\htmltext{ if  }m=0$\cr
A(m-1,1) &$\htmltext{ if   }m>0 \htmltext{  and  } n=0$\cr
A(m-1,A(m,n-1)) &$\htmltext{ if   }m>0 \htmltext{  and  } n>0$\cr
}$$


For example $A(1,0) = 2$, $A(2,2) = 7$ and $A(3,4) = 125$.


Find $\displaystyle\sum_{n=0}^6 A(n,n)$ and give your answer mod $14^8$.

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