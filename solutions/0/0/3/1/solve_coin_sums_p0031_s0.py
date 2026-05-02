#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0031/p0031.py
  func: solve_coin_sums_p0031_s0
"""

from __future__ import annotations

from ast import literal_eval
from sys import argv


def solve(*, coins: list, target_amount: int) -> int:
    result = [1] + [0] * target_amount
    for coin in coins:
        for i in range(coin, target_amount + 1):
            result[i] += result[i - coin]
    return result[-1]


def main() -> int:
    print(solve(coins=literal_eval(argv[1]), target_amount=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
