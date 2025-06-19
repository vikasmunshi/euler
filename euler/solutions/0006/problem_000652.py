#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 652
# https://projecteuler.net/problem=652
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
solution to Project Euler problem 652
https://projecteuler.net/problem=652
Consider the values of $\log_2(8)$, $\log_4(64)$ and $\log_3(27)$. All three are equal to $3$.

Generally, the function $f(m,n)=\log_m(n)$ over integers $m,n \ge 2$ has the property that 

$f(m_1,n_1)=f(m_2,n_2)$ if

$\, m_1=a^e, n_1=a^f, m_2=b^e,n_2=b^f \,$ for some integers $a,b,e,f \, \,$ or 
 $ \, m_1=a^e, n_1=b^e, m_2=a^f,n_2=b^f \,$ for some integers $a,b,e,f \,$ 


We call a function $g(m,n)$ over integers $m,n \ge 2$ proto-logarithmic  if 
$\quad  \, \, \, \, g(m_1,n_1)=g(m_2,n_2)$ if any integers $a,b,e,f$ fulfilling 1. or 2. can be found
and $\, g(m_1,n_1) \ne g(m_2,n_2)$ if no integers $a,b,e,f$ fulfilling 1. or 2. can be found.

Let $D(N)$ be the number of distinct values that any proto-logarithmic function $g(m,n)$ attains over $2\le m, n\le N$.

For example, $D(5)=13$, $D(10)=69$, $D(100)=9607$ and $D(10000)=99959605$.

Find $D(10^{18})$, and give the last $9$ digits as answer.




Note: According to the four exponentials conjecture the function $\log_m(n)$ is proto-logarithmic.
 While this conjecture is yet unproven in general, $\log_m(n)$ can be used to calculate $D(N)$ for small values of $N$.

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