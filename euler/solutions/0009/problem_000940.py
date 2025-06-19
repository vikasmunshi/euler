#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 940
# https://projecteuler.net/problem=940
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
solution to Project Euler problem 940
https://projecteuler.net/problem=940

The Fibonacci sequence $(f_i)$ is the unique sequence such that


$f_0=0$
$f_1=1$
$f_{i+1}=f_i+f_{i-1}$


Similarly, there is a unique function $A(m,n)$ such that


$A(0,0)=0$
$A(0,1)=1$
$A(m+1,n)=A(m,n+1)+A(m,n)$
$A(m+1,n+1)=2A(m+1,n)+A(m,n)$


Define $S(k)=\displaystyle\sum_{i=2}^k\sum_{j=2}^k A(f_i,f_j)$. For example
$$
\begin{align}
S(3)&=A(1,1)+A(1,2)+A(2,1)+A(2,2)\\
&=2+5+7+16\\
&=30
\end{align}
$$You are also given $S(5)=10396$.



Find $S(50)$, giving your answer modulo $1123581313$.


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