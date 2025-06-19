#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 497
# https://projecteuler.net/problem=497
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
solution to Project Euler problem 497
https://projecteuler.net/problem=497
Bob is very familiar with the famous mathematical puzzle/game, "Tower of Hanoi," which consists of three upright rods and disks of different sizes that can slide onto any of the rods. The game begins with a stack of $n$ disks placed on the leftmost rod in descending order by size. The objective of the game is to move all of the disks from the leftmost rod to the rightmost rod, given the following restrictions:

Only one disk can be moved at a time.
A valid move consists of taking the top disk from one stack and placing it onto another stack (or an empty rod).
No disk can be placed on top of a smaller disk.
Moving on to a variant of this game, consider a long room $k$ units (square tiles) wide, labeled from $1$ to $k$ in ascending order. Three rods are placed at squares $a$, $b$, and $c$, and a stack of $n$ disks is placed on the rod at square $a$.

Bob begins the game standing at square $b$. His objective is to play the Tower of Hanoi game by moving all of the disks to the rod at square $c$. However, Bob can only pick up or set down a disk if he is on the same square as the rod/stack in question.

Unfortunately, Bob is also drunk. On a given move, Bob will either stumble one square to the left or one square to the right with equal probability, unless Bob is at either end of the room, in which case he can only move in one direction. Despite Bob's inebriated state, he is still capable of following the rules of the game itself, as well as choosing when to pick up or put down a disk.

The following animation depicts a side-view of a sample game for $n = 3$, $k = 7$, $a = 2$, $b = 4$, and $c = 6$:



Let $E(n, k, a, b, c)$ be the expected number of squares that Bob travels during a single optimally-played game. A game is played optimally if the number of disk-pickups is minimized.

Interestingly enough, the result is always an integer. For example, $E(2,5,1,3,5) = 60$ and $E(3,20,4,9,17) = 2358$.

Find the last nine digits of $\sum_{1\le n \le 10000} E(n,10^n,3^n,6^n,9^n)$.

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