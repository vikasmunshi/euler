#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0031/p0031.py :: solve_coin_sums_p0031_s0.

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
URL: https://projecteuler.net/problem=31"""
from __future__ import annotations

from ast import literal_eval
from sys import argv


def solve(*, coins: list, target_amount: int) -> int:
    result = [1] + [0] * target_amount
    for coin in coins:
        for i in range(coin, target_amount + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    print(solve(coins=literal_eval(argv[1]), target_amount=int(argv[2])))
