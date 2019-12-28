#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=9
A Pythagorean triplet is a set of three natural numbers, a < b < c, for which,

a^2 + b^2 = c^2
For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.

There exists exactly one Pythagorean triplet for which a + b + c = 1000.
Find the product abc.
Answer: 31875000
"""


def special_pythagorean_triplet(sum_sides: int) -> int:
    try:
        return next(a * b * c
                    for a in range(1, sum_sides // 4 + 1)
                    for b in range(a, sum_sides // 2)
                    for c in (sum_sides - a - b,)
                    if a ** 2 + b ** 2 == c ** 2)
    except StopIteration:
        pass


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(special_pythagorean_triplet, answers={12: 60, 1000: 31875000})
