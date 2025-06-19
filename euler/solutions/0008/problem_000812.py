#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 812
# https://projecteuler.net/problem=812
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
solution to Project Euler problem 812
https://projecteuler.net/problem=812
A dynamical polynomial is a monicleading coefficient is $1$ polynomial $f(x)$ with integer coefficients such that $f(x)$ divides $f(x^2-2)$.

For example, $f(x) = x^2 - x - 2$ is a dynamical polynomial because $f(x^2-2) = x^4-5x^2+4 = (x^2 + x -2)f(x)$.

Let $S(n)$ be the number of dynamical polynomials of degree $n$.

For example, $S(2)=6$, as there are six dynamical polynomials of degree $2$:
$$ x^2-4x+4 \quad,\quad x^2-x-2 \quad,\quad x^2-4 \quad,\quad x^2-1 \quad,\quad x^2+x-1 \quad,\quad x^2+2x+1 $$
Also, $S(5)=58$ and $S(20)=122087$.

Find $S(10\,000)$. Give your answer modulo $998244353$.

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