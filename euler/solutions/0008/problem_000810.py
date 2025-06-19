#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 810
# https://projecteuler.net/problem=810
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
solution to Project Euler problem 810
https://projecteuler.net/problem=810
We use $x\oplus y$ for the bitwise XOR of $x$ and $y$.

Define the XOR-product of $x$ and $y$, denoted by $x \otimes y$, similar to a long multiplication in base $2$, except that the intermediate results are XORed instead of the usual integer addition.

For example, $7 \otimes 3 = 9$, or in base $2$, $111_2 \otimes 11_2 = 1001_2$:
$$
\begin{align*}
\phantom{\otimes 111} 111_2 \\
\otimes \phantom{1111} 11_2 \\
\hline
\phantom{\otimes 111} 111_2 \\
\oplus \phantom{11} 111_2  \phantom{9} \\
\hline
\phantom{\otimes 11} 1001_2 \\
\end{align*}
$$

An XOR-prime is an integer $n$ greater than $1$ that is not an XOR-product of two integers greater than $1$. The above example shows that $9$ is not an XOR-prime. Similarly, $5 = 3 \otimes 3$ is not an XOR-prime. The first few XOR-primes are $2, 3, 7, 11, 13, ...$ and the 10th XOR-prime is $41$.

Find the $5\,000\,000$th XOR-prime.

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