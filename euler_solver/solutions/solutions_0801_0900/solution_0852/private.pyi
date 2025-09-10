#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 852: Coins in a Box.

Problem Statement:
    This game has a box of N unfair coins and N fair coins. Fair coins have probability 50%
    of landing heads while unfair coins have probability 75% of landing heads.

    The player begins with a score of 0 which may become negative during play.

    At each round the player randomly picks a coin from the box and guesses its type: fair or
    unfair. Before guessing they may toss the coin any number of times; however, each toss
    subtracts 1 from their score. The decision to stop tossing and make a guess can be made at
    any time. After guessing the player's score is increased by 20 if they are right and
    decreased by 50 if they are wrong. Then the coin type is revealed to the player and the coin
    is discarded.

    After 2N rounds the box will be empty and the game is over. Let S(N) be the expected score
    of the player at the end of the game assuming that they play optimally in order to maximize
    their expected score.

    You are given S(1) = 20.558591 rounded to 6 digits after the decimal point.

    Find S(50). Give your answer rounded to 6 digits after the decimal point.

Solution Approach:
    Use dynamic programming and expected value optimization with probability theory and
    Bayesian updating to decide optimal toss numbers and guessing strategy. Model the states
    by counts of remaining coins and current score. Use floating point computations with careful
    rounding. Complexity is high but manageable by memoization and pruning.

Answer: ...
URL: https://projecteuler.net/problem=852
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 852
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}},
    {'category': 'main', 'input': {'n': 50}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_coins_in_a_box_p0852_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))