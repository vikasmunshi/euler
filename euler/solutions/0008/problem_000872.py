#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 872
# https://projecteuler.net/problem=872
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
solution to Project Euler problem 872
https://projecteuler.net/problem=872
A sequence of rooted trees $T_n$ is constructed such that $T_n$ has $n$ nodes numbered $1$ to $n$.

The sequence starts at $T_1$, a tree with a single node as a root with the number $1$.

For $n > 1$, $T_n$ is constructed from $T_{n-1}$ using the following procedure:

Trace a path from the root of $T_{n-1}$ to a leaf by following the largest-numbered child at each node.
Remove all edges along the traced path, disconnecting all nodes along it from their parents.
Connect all orphaned nodes directly to a new node numbered $n$, which becomes the root of $T_n$.



For example, the following figure shows $T_6$ and $T_7$. The path traced through $T_6$ during the construction of $T_7$ is coloured red.




Let $f(n, k)$ be the sum of the node numbers along the path connecting the root of $T_n$ to the node $k$, including the root and the node $k$. For example, $f(6, 1) = 6 + 5 + 1 = 12$ and $f(10, 3) = 29$.

Find $f(10^{17}, 9^{17})$.



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