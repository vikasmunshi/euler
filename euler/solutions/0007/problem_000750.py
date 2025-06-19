
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 750
# https://projecteuler.net/problem=750
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 750
    https://projecteuler.net/problem=750
    
Card Stacking is a game on a computer starting with an array of $N$ cards labelled $1,2,\ldots,N$.
A stack of cards can be moved by dragging horizontally with the mouse to another stack but only when the resulting stack is in sequence. The goal of the game is to combine the cards into a single stack using minimal total drag distance.






For the given arrangement of 6 cards the minimum total distance is $1 + 3 + 1 + 1 + 2 = 8$.



For $N$ cards, the cards are arranged so that the card at position $n$ is $3^n\bmod(N+1), 1\le n\le N$.


We define $G(N)$ to be the minimal total drag distance to arrange these cards into a single sequence.

For example, when $N = 6$ we get the sequence $3,2,6,4,5,1$ and $G(6) = 8$.

You are given $G(16) = 47$.



Find $G(976)$.



Note: $G(N)$ is not defined for all values of $N$.


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
