#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=26
A unit fraction contains 1 in the numerator.
The decimal representation of the unit fractions with denominators 2 to 10 are given:
1/2	= 	0.5
1/3	= 	0.(3)
1/4	= 	0.25
1/5	= 	0.2
1/6	= 	0.1(6)
1/7	= 	0.(142857)
1/8	= 	0.125
1/9	= 	0.(1)
1/10	= 	0.1
Where 0.1(6) means 0.166666..., and has a 1-digit recurring cycle.
It can be seen that 1/7 has a 6-digit recurring cycle.

Find the value of d < 1000 for which 1/d contains the longest recurring cycle in its decimal fraction part.
Answer: 983
"""
from math import gcd
from typing import Optional


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    r = 1
    for k in range(1, modulus):
        r = (r * a) % modulus
        if r == 1:
            return k


def longest_recurring_cycle(max_val: int) -> int:
    return max((multiplicative_order(10, d), d)
               for i in range(100)
               for d in (max_val - i,)
               if d > 6 and gcd(d, 10) == 1)[1]


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(longest_recurring_cycle, answers={10: 7, 100: 97, 1000: 983})
