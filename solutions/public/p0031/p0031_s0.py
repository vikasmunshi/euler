#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 31: Coin Sums [Level 2]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Unbounded-knapsack coin-change count; O(coins * target_amount) time, O(target_amount) space.

    result[i] holds the unordered ways to make amount i; iterating coins outer and amounts inner
    counts combinations (not permutations), and the upward sweep makes each coin reusable.
    """
    coins = runner.parse_list(args[0])
    target_amount = runner.parse_int(args[1])

    result = [1] + [0] * target_amount
    for coin in coins:
        for i in range(coin, target_amount + 1):
            result[i] += result[i - coin]
    return str(result[-1])


if __name__ == "__main__":
    raise SystemExit(solve())
