#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 325: Stone Game II.

Problem Statement:
    A game is played with two piles of stones and two players.
    On each player's turn the player may remove stones from the larger pile.
    The number removed must be a positive multiple of the smaller pile.
    For example, (6,14) denotes 6 stones in the smaller pile and 14 in the
    larger; the first player can remove 6 or 12 stones from the larger pile.
    The player taking all the stones from a pile wins the game.
    A winning configuration is one where the first player can force a win.
    Examples: (1,5), (2,6) and (3,12) are winning configurations.
    A losing configuration is one where the second player can force a win.
    Examples: (2,3) and (3,4) are losing configurations.
    Define S(N) as the sum of (x_i + y_i) for all losing configurations
    (x_i, y_i) with 0 < x_i < y_i <= N.
    We have S(10) = 211 and S(10^4) = 230312207313.
    Find S(10^16) mod 7^10.

URL: https://projecteuler.net/problem=325
"""
from typing import Any

euler_problem: int = 325
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
