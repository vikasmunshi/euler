#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 499: St. Petersburg Lottery.

Problem Statement:
    A gambler decides to participate in a special lottery. In this lottery the gambler
    plays a series of one or more games.
    Each game costs m pounds to play and starts with an initial pot of 1 pound. The
    gambler flips an unbiased coin. Every time a head appears, the pot is doubled and
    the gambler continues. When a tail appears, the game ends and the gambler collects
    the current value of the pot. The gambler is certain to win at least 1 pound, the
    starting value of the pot, at the cost of m pounds, the initial fee.

    The game ends if the gambler's fortune falls below m pounds.
    Let p_m(s) denote the probability that the gambler will never run out of money
    in this lottery given an initial fortune s and the cost per game m.
    For example p_2(2) ≈ 0.2522, p_2(5) ≈ 0.6873 and p_6(10^4) ≈ 0.9952 (note: p_m(s) = 0
    for s < m).

    Find p_15(10^9) and give your answer rounded to 7 decimal places behind the decimal
    point in the form 0.abcdefg.

URL: https://projecteuler.net/problem=499
"""
from typing import Any

euler_problem: int = 499
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 2, 's': 5}, 'answer': None},
    {'category': 'main', 'input': {'m': 15, 's': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
