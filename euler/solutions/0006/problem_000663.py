#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 663
# https://projecteuler.net/problem=663
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
solution to Project Euler problem 663
https://projecteuler.net/problem=663
Let $t_k$ be the tribonacci numbers defined as: 

$\quad t_0 = t_1 = 0$;

$\quad t_2 = 1$; 

$\quad t_k = t_{k-1} + t_{k-2} + t_{k-3} \quad \text{   for   }  k \ge 3$.

For a given integer $n$, let $A_n$ be an array of length $n$ (indexed from $0$ to $n-1$), that is initially filled with zeros.

The array is changed iteratively by replacing $A_n[(t_{2 i-2} \bmod n)]$ with $A_n[(t_{2 i-2} \bmod n)]+2 (t_{2 i-1} \bmod n)-n+1$ in each step $i$.
 
After each step $i$, define $M_n(i)$ to be $\displaystyle \max\{\sum_{j=p}^q A_n[j]: 0\le p\le q \lt n\}$, the maximal sum of any contiguous subarray of $A_n$. 

The first 6 steps for $n=5$ are illustrated below:

Initial state: $\, A_5=\{0,0,0,0,0\}$

Step 1: $\quad \Rightarrow A_5=\{-4,0,0,0,0\}$, $M_5(1)=0$

Step 2: $\quad \Rightarrow A_5=\{-4, -2, 0, 0, 0\}$, $M_5(2)=0$

Step 3: $\quad \Rightarrow A_5=\{-4, -2, 4, 0, 0\}$, $M_5(3)=4$

Step 4: $\quad \Rightarrow A_5=\{-4, -2, 6, 0, 0\}$, $M_5(4)=6$

Step 5: $\quad \Rightarrow A_5=\{-4, -2, 6, 0, 4\}$, $M_5(5)=10$

Step 6: $\quad \Rightarrow A_5=\{-4, 2, 6, 0, 4\}$, $M_5(6)=12$



Let $\displaystyle S(n,l)=\sum_{i=1}^l M_n(i)$. Thus $S(5,6)=32$.

You are given $S(5,100)=2416$, $S(14,100)=3881$ and $S(107,1000)=1618572$.

Find $S(10\,000\,003,10\,200\,000)-S(10\,000\,003,10\,000\,000)$.

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