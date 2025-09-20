#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 306: Paper-strip Game.

Problem Statement:
    The following game is a classic example of Combinatorial Game Theory:

    Two players start with a strip of n white squares and they take alternate
    turns. On each turn, a player picks two contiguous white squares and
    paints them black. The first player who cannot make a move loses.

    n = 1: No valid moves, so the first player loses automatically.
    n = 2: Only one valid move, after which the second player loses.
    n = 3: Two valid moves, but both leave a situation where the second player
        loses.
    n = 4: Three valid moves for the first player, who is able to win the game
        by painting the two middle squares.
    n = 5: Four valid moves for the first player, but no matter what the
        player does, the second player wins.

    So, for 1 <= n <= 5, there are 3 values of n for which the first player
    can force a win. Similarly, for 1 <= n <= 50, there are 40 such values.

    For 1 <= n <= 1 000 000, how many values of n are there for which the
    first player can force a win?

URL: https://projecteuler.net/problem=306
"""
from typing import Any

euler_problem: int = 306
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
