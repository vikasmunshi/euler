#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=31
In England the currency is made up of pound, £, and pence, p, and there are eight coins in general circulation:

1p, 2p, 5p, 10p, 20p, 50p, £1 (100p) and £2 (200p).
It is possible to make £2 in the following way:

1×£1 + 1×50p + 2×20p + 1×5p + 1×2p + 3×1p
How many different ways can £2 be made using any number of coins?
Answer: 73682
"""


def coin_sum(target: int, coins: (int, ...) = (1, 2, 5, 10, 20, 50, 100, 200)) -> int:
    result = [1] + [0] * target
    for coin in coins:
        for i in range(coin, target + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(func=coin_sum, answers={0: 1, 200: 73682})
