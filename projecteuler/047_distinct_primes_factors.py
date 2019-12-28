#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=47
The first two consecutive numbers to have two distinct prime factors are:

14 = 2 × 7
15 = 3 × 5

The first three consecutive numbers to have three distinct prime factors are:

644 = 2² × 7 × 23
645 = 3 × 5 × 43
646 = 2 × 17 × 19.

Find the first four consecutive integers to have four distinct prime factors each. What is the first of these numbers?
Answer: 134043
"""
from functools import lru_cache
from itertools import count


@lru_cache()
def prime_factor_count(num: int) -> int:
    factor, num_factors = 1, 0
    while factor <= int(num ** 0.5):
        for gap in ([1, 1, 2, 2, 4] if factor < 11 else [2, 4, 2, 4, 6, 2, 6, 4]):
            factor, is_new_factor = factor + gap, True
            while num % factor == 0:
                num //= factor
                if is_new_factor:
                    num_factors, is_new_factor = num_factors + 1, False
    return num_factors + (0 if num == 1 else 1)


def solution(n: int) -> int:
    return next(number for number in count(2) if not any(prime_factor_count(number + i) != n for i in range(0, n)))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(solution, answers={2: 14, 3: 644, 4: 134043})
