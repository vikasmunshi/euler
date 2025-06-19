#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 656
# https://projecteuler.net/problem=656
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
solution to Project Euler problem 656
https://projecteuler.net/problem=656

Given an irrational number $\alpha$, let $S_\alpha(n)$ be the sequence $S_\alpha(n)=\lfloor {\alpha \cdot n} \rfloor - \lfloor {\alpha \cdot (n-1)} \rfloor$ for $n \ge 1$.
 
($\lfloor \cdots \rfloor$ is the floor-function.)


It can be proven that for any irrational $\alpha$ there exist infinitely many values of $n$ such that the subsequence $ \{S_\alpha(1),S_\alpha(2)...S_\alpha(n) \} $ is palindromic.

The first $20$ values of $n$ that give a palindromic subsequence for $\alpha = \sqrt{31}$ are:
$1$, $3$, $5$, $7$, $44$, $81$, $118$, $273$, $3158$, $9201$, $15244$, $21287$, $133765$, $246243$, $358721$, $829920$, $9600319$, $27971037$, $46341755$, $64712473$.

Let $H_g(\alpha)$ be the sum of the first $g$ values of $n$  for which the corresponding subsequence is palindromic.

So $H_{20}(\sqrt{31})=150243655$.

Let $T=\{2,3,5,6,7,8,10,...,1000\}$ be the set of positive integers, not exceeding $1000$, excluding perfect squares.

Calculate the sum of $H_{100}(\sqrt \beta)$ for  $\beta \in T$. Give the last $15$ digits of your answer.



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