#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 509: Divisor Nim.

Problem Statement:
    Anton and Bertrand love to play three pile Nim.
    However, after a lot of games of Nim they got bored and changed the rules somewhat.
    They may only take a number of stones from a pile that is a proper divisor of the
    number of stones present in the pile.
    E.g. if a pile at a certain moment contains 24 stones they may take only 1, 2, 3, 4,
    6, 8 or 12 stones from that pile.
    So if a pile contains one stone they can't take the last stone from it as 1 isn't a
    proper divisor of 1.
    The first player that can't make a valid move loses the game.
    Both Anton and Bertrand play optimally.

    The triple (a, b, c) indicates the number of stones in the three piles.
    Let S(n) be the number of winning positions for the next player for 1 ≤ a, b, c ≤ n.
    S(10) = 692 and S(100) = 735494.

    Find S(123456787654321) modulo 1234567890.

URL: https://projecteuler.net/problem=509
"""
from typing import Any

euler_problem: int = 509
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 123456787654321}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
