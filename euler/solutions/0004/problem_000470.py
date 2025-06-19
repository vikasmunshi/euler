#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 470
# https://projecteuler.net/problem=470
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
solution to Project Euler problem 470
https://projecteuler.net/problem=470
Consider a single game of Ramvok:

Let $t$ represent the maximum number of turns the game lasts. If $t = 0$, then the game ends immediately. Otherwise, on each turn $i$, the player rolls a die. After rolling, if $i \lt t$ the player can either stop the game and receive a prize equal to the value of the current roll, or discard the roll and try again next turn. If $i = t$, then the roll cannot be discarded and the prize must be accepted. Before the game begins, $t$ is chosen by the player, who must then pay an up-front cost $ct$ for some constant $c$. For $c = 0$, $t$ can be chosen to be infinite (with an up-front cost of $0$). Let $R(d, c)$ be the expected profit (i.e. net gain) that the player receives from a single game of optimally-played Ramvok, given a fair $d$-sided die and cost constant $c$. For example, $R(4, 0.2) = 2.65$. Assume that the player has sufficient funds for paying any/all up-front costs.

Now consider a game of Super Ramvok:

In Super Ramvok, the game of Ramvok is played repeatedly, but with a slight modification. After each game, the die is altered. The alteration process is as follows: The die is rolled once, and if the resulting face has its pips visible, then that face is altered to be blank instead. If the face is already blank, then it is changed back to its original value. After the alteration is made, another game of Ramvok can begin (and during such a game, at each turn, the die is rolled until a face with a value on it appears). The player knows which faces are blank and which are not at all times. The game of Super Ramvok ends once all faces of the die are blank.

Let $S(d, c)$ be the expected profit that the player receives from an optimally-played game of Super Ramvok, given a fair $d$-sided die to start (with all sides visible), and cost constant $c$. For example, $S(6, 1) = 208.3$.

Let $F(n) = \sum_{4 \le d \le n} \sum_{0 \le c \le n} S(d, c)$.

Calculate $F(20)$, rounded to the nearest integer.

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