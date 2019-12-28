#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=1
If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9.
The sum of these multiples is 23.

Find the sum of all the multiples of 3 or 5 below 1000.
Answer: 233168
"""


def sum_multiples_3_and_5(max_limit: int) -> int:
    def sum_multiples(number: int) -> int:
        terms = (max_limit - 1) // number
        return number * terms * (terms + 1) // 2

    return sum_multiples(3) + sum_multiples(5) - sum_multiples(3 * 5)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(sum_multiples_3_and_5, answers={10: 23, 1000: 233168})
