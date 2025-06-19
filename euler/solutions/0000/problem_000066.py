#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 66
# https://projecteuler.net/problem=66
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
solution to Project Euler problem 66
https://projecteuler.net/problem=66
Consider quadratic Diophantine equations of the form:
$$x^2 - Dy^2 = 1$$
For example, when $D=13$, the minimal solution in $x$ is $649^2 - 13 \times 180^2 = 1$.
It can be assumed that there are no solutions in positive integers when $D$ is square.
By finding minimal solutions in $x$ for $D = \{2, 3, 5, 6, 7\}$, we obtain the following:
\begin{align}
3^2 - 2 \times 2^2 &= 1\\
2^2 - 3 \times 1^2 &= 1\\
{\color{red}{\mathbf 9}}^2 - 5 \times 4^2 &= 1\\
5^2 - 6 \times 2^2 &= 1\\
8^2 - 7 \times 3^2 &= 1
\end{align}
Hence, by considering minimal solutions in $x$ for $D \le 7$, the largest $x$ is obtained when $D=5$.
Find the value of $D \le 1000$ in minimal solutions of $x$ for which the largest value of $x$ is obtained.


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