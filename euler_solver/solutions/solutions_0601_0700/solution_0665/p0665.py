#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 665: Proportionate Nim.

Problem Statement:
    Two players play a game with two piles of stones, alternating turns.

    On each turn, the corresponding player chooses a positive integer n and does one of the
    following:
        removes n stones from one pile;
        removes n stones from both piles; or
        removes n stones from one pile and 2n stones from the other pile.

    The player who removes the last stone wins.

    We denote by (n,m) the position in which the piles have n and m stones remaining. Note
    that (n,m) is considered to be the same position as (m,n).

    Then, for example, if the position is (2,6), the next player may reach the following
    positions:
    (0,2), (0,4), (0,5), (0,6), (1,2), (1,4), (1,5), (1,6), (2,2), (2,3), (2,4), (2,5).

    A position is a losing position if the player to move next cannot force a win. For example,
    (1,3), (2,6), (4,5) are the first few losing positions.

    Let f(M) be the sum of n+m for all losing positions (n,m) with n <= m and n+m <= M. For
    example, f(10) = 21, by considering the losing positions (1,3), (2,6), (4,5).

    You are given that f(100) = 1164 and f(1000) = 117002.

    Find f(10^7).

URL: https://projecteuler.net/problem=665
"""
from typing import Any

euler_problem: int = 665
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
