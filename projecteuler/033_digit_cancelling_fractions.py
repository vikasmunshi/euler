#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=33
The fraction 49/98 is a curious fraction, as an inexperienced mathematician in attempting to simplify it may
incorrectly believe that 49/98 = 4/8, which is correct, is obtained by cancelling the 9s.

We shall consider fractions like, 30/50 = 3/5, to be trivial examples.

There are exactly four non-trivial examples of this type of fraction, less than one in value, and containing two digits
in the numerator and denominator.

If the product of these four fractions is given in its lowest common terms, find the value of the denominator.
Answer: 100
"""
from fractions import Fraction
from functools import reduce


def solution() -> int:
    return reduce(
        lambda a, b: a * b,
        [Fraction(numerator, denominator)
         for denominator in range(2, 10)
         for numerator in range(1, denominator)
         for x in range(1, 10) if denominator != x != numerator
         if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator],
        1
    ).denominator


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(func=solution)(answer=100)
