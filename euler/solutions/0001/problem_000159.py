#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 159
# https://projecteuler.net/problem=159
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
solution to Project Euler problem 159
https://projecteuler.net/problem=159
A composite number can be factored many different ways.  
For instance, not including multiplication by one, $24$ can be factored in $7$ distinct ways:
\begin{align}
24 &= 2 \times 2 \times 2 \times 3\\
24 &= 2 \times 3 \times 4\\
24 &= 2 \times 2 \times 6\\
24 &= 4 \times 6\\
24 &= 3 \times 8\\
24 &= 2 \times 12\\
24 &= 24
\end{align}

Recall that the digital root of a number, in base $10$, is found by adding together the digits of that number, 
and repeating that process until a number is arrived at that is less than $10$.  
Thus the digital root of $467$ is $8$.
We shall call a Digital Root Sum (DRS) the sum of the digital roots of the individual factors of our number.

The chart below demonstrates all of the DRS values for $24$.

FactorisationDigital Root Sum
$2 \times 2 \times 2 \times 3$$9$
$2 \times 3 \times 4$$9$
$2 \times 2 \times 6$$10$
$4 \times 6$$10$
$3 \times 8$$11$
$2 \times 12$$5$
$24$$6$

The maximum Digital Root Sum of $24$ is $11$.

The function $\operatorname{mdrs}(n)$ gives the maximum Digital Root Sum of $n$. So $\operatorname{mdrs}(24)=11$.

Find $\sum \operatorname{mdrs}(n)$ for $1 \lt n \lt 1\,000\,000$.

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