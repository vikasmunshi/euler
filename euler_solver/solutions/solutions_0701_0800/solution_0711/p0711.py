#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 711: Binary Blackboard.

Problem Statement:
    Oscar and Eric play the following game. First, they agree on a positive integer n,
    and they begin by writing its binary representation on a blackboard. They then take
    turns, with Oscar going first, to write a number on the blackboard in binary
    representation, such that the sum of all written numbers does not exceed 2n.

    The game ends when there are no valid moves left. Oscar wins if the number of 1s
    on the blackboard is odd, and Eric wins if it is even.

    Let S(N) be the sum of all n ≤ 2^N for which Eric can guarantee winning, assuming
    optimal play.

    For example, the first few values of n for which Eric can guarantee winning are
    1, 3, 4, 7, 15, 16. Hence S(4) = 46.
    You are also given that S(12) = 54532 and S(1234) ≡ 690421393 (mod 1,000,000,007).

    Find S(12345678). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=711
"""
from typing import Any

euler_problem: int = 711
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 4}, 'answer': None},
    {'category': 'main', 'input': {'N': 12345678}, 'answer': None},
    {'category': 'extra', 'input': {'N': 1234}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
