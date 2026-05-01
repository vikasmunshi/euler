#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 366: Stone Game III.

Problem Statement:
    Two players, Anton and Bernhard, are playing the following game.
    There is one pile of n stones.
    The first player may remove any positive number of stones, but not the whole pile.
    Thereafter, each player may remove at most twice the number of stones his opponent
    took on the previous move.
    The player who removes the last stone wins.

    E.g. n = 5.
    If the first player takes anything more than one stone the next player will be able
    to take all remaining stones.
    If the first player takes one stone, leaving four, his opponent will take also one
    stone, leaving three stones.
    The first player cannot take all three because he may take at most 2 x 1 = 2 stones.
    So let's say he takes also one stone, leaving 2. The second player can take the
    two remaining stones and wins.
    So 5 is a losing position for the first player.
    For some winning positions there is more than one possible move for the first
    player. E.g. when n = 17 the first player can remove one or four stones.

    Let M(n) be the maximum number of stones the first player can take from a winning
    position at his first turn and M(n) = 0 for any other position.

    Sum M(n) for n <= 100 is 728.

    Find sum M(n) for n <= 1000000000000000000. Give your answer modulo 100000000.

URL: https://projecteuler.net/problem=366
"""
from typing import Any

euler_problem: int = 366
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100, 'mod': 100000000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000, 'mod': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000, 'mod': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
