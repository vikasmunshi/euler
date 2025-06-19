
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 720
# https://projecteuler.net/problem=720
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 720
    https://projecteuler.net/problem=720
    Consider all permutations of $\{1, 2, \ldots N\}$, listed in lexicographic order.
For example, for $N=4$, the list starts as follows:

$$\displaylines{
(1, 2, 3, 4) \\
(1, 2, 4, 3) \\
(1, 3, 2, 4) \\
(1, 3, 4, 2) \\
(1, 4, 2, 3) \\
(1, 4, 3, 2) \\
(2, 1, 3, 4) \\
\vdots
}$$


Let us call a permutation $P$ unpredictable if there is no choice of three indices $i \lt j \lt k$ such that $P(i)$, $P(j)$ and $P(k)$ constitute an arithmetic progression.
 For example, $P=(3, 4, 2, 1)$ is not unpredictable because $P(1), P(3), P(4)$ is an arithmetic progression.


Let $S(N)$ be the position within the list of the first unpredictable permutation.



For example, given $N = 4$, the first unpredictable permutation is $(1, 3, 2, 4)$ so $S(4) = 3$.

You are also given that $S(8) = 2295$ and $S(32) \equiv 641839205 \pmod{1\,000\,000\,007}$.


Find $S(2^{25})$. Give your answer modulo $1\,000\,000\,007$.


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
