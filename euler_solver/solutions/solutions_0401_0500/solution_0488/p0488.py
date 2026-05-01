#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 488: Unbalanced Nim.

Problem Statement:
    Alice and Bob have enjoyed playing Nim every day. However, they finally got bored
    of playing ordinary three-heap Nim.
    So, they added an extra rule:
    - Must not make two heaps of the same size.

    The triple (a, b, c) indicates the size of three heaps.
    Under this extra rule, (2,4,5) is one of the losing positions for the next player.

    To illustrate:
    - Alice moves to (2,4,3)
    - Bob   moves to (0,4,3)
    - Alice moves to (0,2,3)
    - Bob   moves to (0,2,1)

    Unlike ordinary three-heap Nim, (0,1,2) and its permutations are the end states of
    this game.

    For an integer N, we define F(N) as the sum of a + b + c for all the losing positions
    for the next player, with 0 < a < b < c < N.

    For example, F(8) = 42, because there are 4 losing positions for the next player,
    (1,3,5), (1,4,6), (2,3,6) and (2,4,5).
    We can also verify that F(128) = 496062.

    Find the last 9 digits of F(10^18).

URL: https://projecteuler.net/problem=488
"""
from typing import Any

euler_problem: int = 488
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
