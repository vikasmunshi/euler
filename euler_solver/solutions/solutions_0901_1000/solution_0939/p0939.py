#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 939: Partisan Nim.

Problem Statement:
    Two players A and B are playing a variant of Nim.
    At the beginning, there are several piles of stones. Each pile is either at
    the side of A or at the side of B. The piles are unordered.

    They make moves in turn. At a player's turn, the player can
        either choose a pile on the opponent's side and remove one stone from
        that pile;
        or choose a pile on their own side and remove the whole pile.
    The winner is the player who removes the last stone.

    Let E(N) be the number of initial settings with at most N stones such that,
    whoever plays first, A always has a winning strategy.

    For example E(4) = 9; the settings are:

    Nr.  Piles at the side of A    Piles at the side of B
    1    4                        none
    2    1, 3                     none
    3    2, 2                     none
    4    1, 1, 2                  none
    5    3                        1
    6    1, 2                     1
    7    2                        1, 1
    8    3                        none
    9    2                        none

    Find E(5000) mod 1234567891.

URL: https://projecteuler.net/problem=939
"""
from typing import Any

euler_problem: int = 939
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
    'RBcZ1A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
