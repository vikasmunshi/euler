#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 751
# https://projecteuler.net/problem=751
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
solution to Project Euler problem 751
https://projecteuler.net/problem=751
A non-decreasing sequence of integers $a_n$ can be generated from any positive real value $\theta$ by the following procedure:
\begin{align}
\begin{split}
b_1 &= \theta \\
b_n &= \left\lfloor b_{n-1} \right\rfloor \left(b_{n-1} - \left\lfloor b_{n-1} \right\rfloor + 1\right)~~~\forall ~ n \geq 2 \\
a_n &= \left\lfloor b_{n} \right\rfloor
\end{split}
\end{align}
Where $\left\lfloor \cdot \right\rfloor$ is the floor function.

For example, $\theta=2.956938891377988...$ generates the Fibonacci sequence: $2, 3, 5, 8, 13, 21, 34, 55, 89, ...$

The concatenation of a sequence of positive integers $a_n$ is a real value denoted $\tau$ constructed by concatenating the elements of the sequence after the decimal point, starting at $a_1$: $a_1.a_2a_3a_4...$

For example, the Fibonacci sequence constructed from $\theta=2.956938891377988...$ yields the concatenation $\tau=2.3581321345589...$ Clearly, $\tau \neq \theta$ for this value of $\theta$.

Find the only value of $\theta$ for which the generated sequence starts at $a_1=2$ and the concatenation of the generated sequence equals the original value: $\tau = \theta$. Give your answer rounded to $24$ places after the decimal point.

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