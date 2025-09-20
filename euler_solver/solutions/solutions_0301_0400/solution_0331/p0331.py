#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 331: Cross Flips.

Problem Statement:
    N x N disks are placed on a square game board. Each disk has a black side
    and a white side.

    At each turn you may choose a disk and flip all the disks in the same row
    and the same column as this disk; thus 2*N - 1 disks are flipped. The game
    ends when all disks show their white side. An example on a 5 x 5 board
    can be finished in 3 turns.

    The bottom left disk has coordinates (0,0); the bottom right is (N-1,0)
    and the top left is (0,N-1).

    Let C_N be the configuration where a disk at (x, y) with
    N - 1 <= sqrt(x^2 + y^2) < N shows its black side, otherwise it is white.
    Let T(N) be the minimal number of turns to finish the game from C_N, or 0
    if C_N is unsolvable. We are given T(5)=3, T(10)=29 and T(1000)=395253.

    Find sum_{i = 3}^{31} T(2^i - i).

URL: https://projecteuler.net/problem=331
"""
from typing import Any

euler_problem: int = 331
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'i_start': 3, 'i_end': 3}, 'answer': None},
    {'category': 'main', 'input': {'i_start': 3, 'i_end': 31}, 'answer': None},
    {'category': 'extra', 'input': {'i_start': 3, 'i_end': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
