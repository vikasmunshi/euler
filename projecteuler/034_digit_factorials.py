#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=34
145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.

Find the sum of all numbers which are equal to the sum of the factorial of their digits.

Note: as 1! = 1 and 2! = 2 are not sums they are not included.
Answer: 40730
"""
from itertools import combinations_with_replacement


def solution() -> int:
    upper_bound_num_digits = 7
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum(
        int(num)
        for num_digits in range(2, upper_bound_num_digits + 1)
        for digits in combinations_with_replacement('0123456789', num_digits)
        for num in (str(sum(factorial[d] for d in digits)),)
        if len(num) == num_digits
        and all(digit in num for digit in digits)
        and num == str(sum(factorial[n] for n in num))
    )


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(func=solution)(answer=40730)
