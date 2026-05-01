#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 550: Divisor Game.

Problem Statement:
    Two players are playing a game, alternating turns. There are k piles of stones.
    On each turn, a player has to choose a pile and replace it with two piles of stones
    under the following two conditions:

        Both new piles must have a number of stones more than one and less than the
        number of stones of the original pile.
        The number of stones of each of the new piles must be a divisor of the number
        of stones of the original pile.

    The first player unable to make a valid move loses.

    Let f(n,k) be the number of winning positions for the first player, assuming perfect
    play, when the game is played with k piles each having between 2 and n stones
    (inclusively).
    f(10,5) = 40085.

    Find f(10^7, 10^12).
    Give your answer modulo 987654321.

URL: https://projecteuler.net/problem=550
"""
from typing import Any

euler_problem: int = 550
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'k': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 'k': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'kPYHpMXLLAth4qXc'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
