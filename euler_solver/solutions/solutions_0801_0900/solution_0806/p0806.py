#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 806: Nim on Towers of Hanoi.

Problem Statement:
    This problem combines the game of Nim with the Towers of Hanoi. For a brief
    introduction to the rules of these games, please refer to Problem 301 and
    Problem 497, respectively.

    The unique shortest solution to the Towers of Hanoi problem with n disks and
    3 pegs requires 2^n - 1 moves. Number the positions in the solution from index
    0 (starting position, all disks on the first peg) to index 2^n - 1 (final position,
    all disks on the third peg).

    Each of these 2^n positions can be considered as the starting configuration
    for a game of Nim, in which two players take turns to select a peg and remove
    any positive number of disks from it. The winner is the player who removes
    the last disk.

    We define f(n) to be the sum of the indices of those positions for which,
    when considered as a Nim game, the first player will lose (assuming an optimal
    strategy from both players).

    For n=4, the indices of losing positions in the shortest solution are 3, 6, 9
    and 12. So we have f(4) = 30.

    You are given that f(10) = 67518.

    Find f(10^5). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=806
"""
from typing import Any

euler_problem: int = 806
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
    'cRkXp7eOFQeVMReDxPVnQBEgjpBbFGzv'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
