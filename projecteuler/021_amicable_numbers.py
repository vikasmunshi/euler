#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=21
Let d(n) be defined as the sum of proper divisors of n (numbers less than n which divide evenly into n).
If d(a) = b and d(b) = a, where a ≠ b,
then a and b are an amicable pair and each of a and b are called amicable numbers.

For example, the proper divisors of 220 are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55 and 110; therefore d(220) = 284.
The proper divisors of 284 are 1, 2, 4, 71 and 142; so d(284) = 220.

Evaluate the sum of all the amicable numbers under 10000.
Answer: 31626
"""
from functools import lru_cache


def sum_amicable_numbers(max_num: int) -> int:
    @lru_cache()
    def sum_factors(n: int) -> int:
        n_sqrt = int(n ** 0.5)
        return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)

    return sum(x for x in range(2, max_num + 1) if sum_factors(x) != x and sum_factors(sum_factors(x)) == x)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(sum_amicable_numbers, answers={10000: 31626})
