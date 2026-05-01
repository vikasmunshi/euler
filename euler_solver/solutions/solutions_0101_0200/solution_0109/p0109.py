#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 109: Darts.

Problem Statement:
    In the game of darts a player throws three darts at a target board which is
    split into twenty equal sized sections numbered one to twenty.

    The score of a dart is determined by the number of the region that the dart
    lands in. A dart landing outside the red/green outer ring scores zero. The
    black and cream regions inside this ring represent single scores. However, the
    red/green outer ring and middle ring score double and treble scores respectively.

    At the centre of the board are two concentric circles called the bull region, or
    bulls-eye. The outer bull is worth 25 points and the inner bull is a double, worth
    50 points.

    There are many variations of rules but in the most popular game the players will
    begin with a score 301 or 501 and the first player to reduce their running total
    to zero is a winner. However, it is normal to play a "doubles out" system, which
    means that the player must land a double (including the double bulls-eye at the
    centre of the board) on their final dart to win; any other dart that would reduce
    their running total to one or lower means the score for that set of three darts is
    "bust".

    When a player is able to finish on their current score it is called a "checkout"
    and the highest checkout is 170: T20 T20 D25 (two treble 20s and double bull).

    There are exactly eleven distinct ways to checkout on a score of 6:

        D3
        D1 D2
        S2 D2
        D2 D1
        S4 D1
        S1 S1 D2
        S1 T1 D1
        S1 S3 D1
        D1 D1 D1
        D1 S2 D1
        S2 S2 D1

    Note that D1 D2 is considered different to D2 D1 as they finish on different doubles.
    However, the combination S1 T1 D1 is considered the same as T1 S1 D1.

    In addition we shall not include misses in considering combinations; for example, D3
    is the same as 0 D3 and 0 0 D3.

    Incredibly there are 42336 distinct ways of checking out in total.

    How many distinct ways can a player checkout with a score less than 100?

URL: https://projecteuler.net/problem=109
"""
from typing import Any

euler_problem: int = 109
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
