#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 391: Hopping Game.

Problem Statement:
    Let s_k be the number of 1's when writing the numbers from 0 to k in
    binary.

    For example, writing 0 to 5 in binary, we have 0, 1, 10, 11, 100, 101.
    There are seven 1's, so s_5 = 7.

    The sequence S = {s_k : k >= 0} starts {0, 1, 2, 4, 5, 7, 9, 12, ...}.

    A game is played by two players. Before the game starts, a number n is
    chosen. A counter c starts at 0. At each turn, the player chooses a number
    from 1 to n (inclusive) and increases c by that number. The resulting
    value of c must be a member of S. If there are no more valid moves, then
    the player loses.

    For example, with n = 5 and starting with c = 0:
    Player 1 chooses 4, so c becomes 0 + 4 = 4.
    Player 2 chooses 5, so c becomes 4 + 5 = 9.
    Player 1 chooses 3, so c becomes 9 + 3 = 12.
    etc.

    Note that c must always belong to S, and each player can increase c by
    at most n.

    Let M(n) be the highest number that the first player could choose at the
    start to force a win, and M(n) = 0 if there is no such move. For example,
    M(2) = 2, M(7) = 1, and M(20) = 4.

    It can be verified that sum M(n)^3 = 8150 for 1 <= n <= 20.

    Find sum M(n)^3 for 1 <= n <= 1000.

URL: https://projecteuler.net/problem=391
"""
from typing import Any

euler_problem: int = 391
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Z6Lhh7jdi3U='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
