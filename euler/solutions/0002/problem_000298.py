#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 298
# https://projecteuler.net/problem=298
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
solution to Project Euler problem 298
https://projecteuler.net/problem=298
Larry and Robin play a memory game involving a sequence of random numbers between 1 and 10, inclusive, that are called out one at a time. Each player can remember up to 5 previous numbers. When the called number is in a player's memory, that player is awarded a point. If it's not, the player adds the called number to his memory, removing another number if his memory is full.

Both players start with empty memories. Both players always add new missed numbers to their memory but use a different strategy in deciding which number to remove:

Larry's strategy is to remove the number that hasn't been called in the longest time.

Robin's strategy is to remove the number that's been in the memory the longest time.

Example game:
Turn
  Called
number
  Larry's
memory
  Larry's
score
  Robin's
memory
  Robin's
score
1
  1
  1
  0
  1
  0
2
  2
  1,2
  0
  1,2
  0
3
  4
  1,2,4
  0
  1,2,4
  0
4
  6
  1,2,4,6
  0
  1,2,4,6
  0
5
  1
  1,2,4,6
  1
  1,2,4,6
  1
6
  8
  1,2,4,6,8
  1
  1,2,4,6,8
  1
7
  10
  1,4,6,8,10
  1
  2,4,6,8,10
  1
8
  2
  1,2,6,8,10
  1
  2,4,6,8,10
  2
9
  4
  1,2,4,8,10
  1
  2,4,6,8,10
  3
10
  1
  1,2,4,8,10
  2
  1,4,6,8,10
  3
Denoting Larry's score by L and Robin's score by R, what is the expected value of |L-R| after 50 turns? Give your answer rounded to eight decimal places using the format x.xxxxxxxx .

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