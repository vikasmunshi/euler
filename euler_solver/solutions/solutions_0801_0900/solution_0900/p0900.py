#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 900: DistribuNim II.

Problem Statement:
    Two players play a game with at least two piles of stones. The players alternately
    take stones from one or more piles, subject to:

        1. the total number of stones taken is equal to the size of the smallest pile
           before the move;

        2. the move cannot take all the stones from a pile.

    The player that is unable to move loses.

    For example, if the piles are of sizes 2, 2 and 4 then there are four possible moves.
    (2,2,4) -> (1,1,4) by taking (1,1,0)
    (2,2,4) -> (1,2,3) by taking (1,0,1)
    (2,2,4) -> (2,1,3) by taking (0,1,1)
    (2,2,4) -> (2,2,2) by taking (0,0,2)

    Let t(n) be the smallest nonnegative integer k such that the position with n piles
    of n stones and a single pile of n+k stones is losing for the first player assuming
    optimal play. For example, t(1) = t(2) = 0 and t(3) = 2.

    Define S(N) = sum of t(n) for n = 1 to 2^N. You are given S(10) = 361522.

    Find S(10^4). Give your answer modulo 900497239.

URL: https://projecteuler.net/problem=900
"""
from typing import Any

euler_problem: int = 900
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 2}, 'answer': None},
    {'category': 'main', 'input': {'N': 10}, 'answer': None},
    {'category': 'extra', 'input': {'N': 14}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
