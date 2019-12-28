#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=20
n! means n × (n − 1) × ... × 3 × 2 × 1

For example, 10! = 10 × 9 × ... × 3 × 2 × 1 = 3628800,
and the sum of the digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

Find the sum of the digits in the number 100!
Answer: 648
"""
from math import factorial


def factorial_digit_sum(n: int) -> int:
    return sum(int(d) for d in str(factorial(n)))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(factorial_digit_sum, answers={10: 27, 100: 648})
