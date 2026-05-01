#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 31: Coin Sums.

Problem Statement:
    In the United Kingdom the currency is made up of pound (£) and pence (p). There are
    eight coins in general circulation:

    1p, 2p, 5p, 10p, 20p, 50p, £1 (100p), and £2 (200p).

    It is possible to make £2 in the following way:

    1×£1 + 1×50p + 2×20p + 1×5p + 1×2p + 3×1p

    How many different ways can £2 be made using any number of coins?

Solution Approach:
    Use dynamic programming or combinatorics counting. Model the problem as counting
    the number of ways to make a sum (200p) using unlimited supply of fixed coin values.
    Use an integer partition or coin change approach with a DP table.
    Expected time complexity: O(n * m) where n=200 and m=number of coin types.

Answer: 73682
URL: https://projecteuler.net/problem=31
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 31
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target_amount': 0},
     'answer': 1},
    {'category': 'main', 'input': {'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target_amount': 200},
     'answer': 73682},
    {'category': 'extra', 'input': {'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target_amount': 1000},
     'answer': 321335886},
    {'category': 'extra', 'input': {'coins': [1, 2, 5, 10, 20, 50, 100, 200], 'target_amount': 100000},
     'answer': 10056050940818192726001},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_coin_sums_p0031_s0(*, coins: list, target_amount: int) -> int:
    result = [1] + [0] * target_amount
    for coin in coins:
        for i in range(coin, target_amount + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
