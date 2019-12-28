#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=24
A permutation is an ordered arrangement of objects.
For example, 3124 is one possible permutation of the digits 1, 2, 3 and 4.
If all of the permutations are listed numerically or alphabetically, we call it lexicographic order.
The lexicographic permutations of 0, 1 and 2 are:

012   021   102   120   201   210

What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4, 5, 6, 7, 8 and 9?
Answer: 2783915460
"""
from math import factorial


def nth_lexicographic_permutation(digits: str, permutation_number: int) -> str:
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))
    return digits[current] + nth_lexicographic_permutation(digits[:current] + digits[current + 1:], remaining + 1)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate(nth_lexicographic_permutation)('0123456789', 10 ** 6, answer='2783915460')
