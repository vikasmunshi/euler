#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=32
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n exactly once; for example,
the 5-digit number, 15234, is 1 through 5 pandigital.

The product 7254 is unusual, as the identity, 39 × 186 = 7254, containing multiplicand, multiplier,
and product is 1 through 9 pandigital.

Find the sum of all products whose multiplicand/multiplier/product identity can be written as a 1 through 9 pandigital.

HINT: Some products can be obtained in more than one way so be sure to only include it once in your sum.
Answer: 45228
"""
from itertools import permutations

digits = ('1', '2', '3', '4', '5', '6', '7', '8', '9')


def sum_pandigital_products() -> int:
    return sum(set(c
                   for a_len, b_len in ((1, 4), (2, 3))
                   for a in permutations(digits, a_len)
                   for b in permutations((d for d in digits if d not in a), b_len)
                   for a_str, b_str in ((''.join(a), ''.join(b)),)
                   for c in ((int(a_str) * int(b_str)),)
                   if ''.join(sorted(a_str + b_str + str(c))) == '123456789'))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(func=sum_pandigital_products)(answer=45228)
