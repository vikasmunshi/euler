
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 74
# https://projecteuler.net/problem=74
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 74
    https://projecteuler.net/problem=74
    The number $145$ is well known for the property that the sum of the factorial of its digits is equal to $145$:
$$1! + 4! + 5! = 1 + 24 + 120 = 145.$$
Perhaps less well known is $169$, in that it produces the longest chain of numbers that link back to $169$; it turns out that there are only three such loops that exist:
\begin{align}
&169 \to 363601 \to 1454 \to 169\\
&871 \to 45361 \to 871\\
&872 \to 45362 \to 872
\end{align}
It is not difficult to prove that EVERY starting number will eventually get stuck in a loop. For example,
\begin{align}
&69 \to 363600 \to 1454 \to 169 \to 363601 (\to 1454)\\
&78 \to 45360 \to 871 \to 45361 (\to 871)\\
&540 \to 145 (\to 145)
\end{align}
Starting with $69$ produces a chain of five non-repeating terms, but the longest non-repeating chain with a starting number below one million is sixty terms.
How many chains, with a starting number below one million, contain exactly sixty non-repeating terms?


    """
    raise NotImplementedError


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
