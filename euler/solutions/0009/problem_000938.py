
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 938
# https://projecteuler.net/problem=938
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 938
    https://projecteuler.net/problem=938
    
A deck of cards contains $R$ red cards and $B$ black cards.

A card is chosen uniformly randomly from the deck and removed. A second card is then chosen uniformly randomly from the cards remaining and removed.


If both cards are red, they are discarded.

If both cards are black, they are both put back in the deck.

If they are different colours, the red card is put back in the deck and the black card is discarded.

Play ends when all the remaining cards in the deck are the same colour and let $P(R,B)$ be the probability that this colour is black. 

You are given $P(2,2) = 0.4666666667$, $P(10,9) = 0.4118903397$ and $P(34,25) = 0.3665688069$.

Find $P(24690,12345)$. Give your answer with 10 digits after the decimal point.

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
