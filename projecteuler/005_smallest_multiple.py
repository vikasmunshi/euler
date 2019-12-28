#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=5
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.

What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20?
Answer: 232792560
"""
from functools import reduce
from math import gcd


def smallest_multiple(n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(smallest_multiple, answers={10: 2520, 20: 232792560})
