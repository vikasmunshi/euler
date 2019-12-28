#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=16
2^15 = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.

What is the sum of the digits of the number 2^1000?
Answer: 1366
"""


def power_digits_sum(power: int, base: int = 2) -> int:
    return sum(int(i) for i in str(base ** power))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(power_digits_sum, answers={15: 26, 1000: 1366})
