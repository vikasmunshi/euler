#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 629: Scatterstone Nim.

Problem Statement:
    Alice and Bob are playing a modified game of Nim called Scatterstone Nim, with Alice
    going first, alternating turns with Bob. The game begins with an arbitrary set of
    stone piles with a total number of stones equal to n.

    During a player's turn, he/she must pick a pile having at least 2 stones and perform
    a split operation, dividing the pile into an arbitrary set of p non-empty,
    arbitrarily-sized piles where 2 ≤ p ≤ k for some fixed constant k. For example, a
    pile of size 4 can be split into {1, 3} or {2, 2}, or {1, 1, 2} if k = 3 and in
    addition {1, 1, 1, 1} if k = 4.

    If no valid move is possible on a given turn, then the other player wins the game.

    A winning position is defined as a set of stone piles where a player can ultimately
    ensure victory no matter what the other player does.

    Let f(n, k) be the number of winning positions for Alice on her first turn, given
    parameters n and k. For example, f(5, 2) = 3 with winning positions {1, 1, 1, 2},
    {1, 4}, {2, 3}. In contrast, f(5, 3) = 5 with winning positions {1, 1, 1, 2},
    {1, 1, 3}, {1, 4}, {2, 3}, {5}.

    Let g(n) be the sum of f(n, k) over all 2 ≤ k ≤ n. For example, g(7) = 66 and
    g(10) = 291.

    Find g(200) mod (10^9 + 7).

URL: https://projecteuler.net/problem=629
"""
from typing import Any

euler_problem: int = 629
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'qvBsD2nV5S3xiOQbpJKfVIoYJoGYN3BF'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
