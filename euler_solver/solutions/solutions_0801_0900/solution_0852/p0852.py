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

URL: https://projecteuler.net/problem=852
"""
from typing import Any

euler_problem: int = 852
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
