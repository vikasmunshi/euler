#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=44
Pentagonal numbers are generated by the formula, Pn=n(3n−1)/2. The first ten pentagonal numbers are:

1, 5, 12, 22, 35, 51, 70, 92, 117, 145, ...

It can be seen that P4 + P7 = 22 + 70 = 92 = P8. However, their difference, 70 − 22 = 48, is not pentagonal.

Find the pair of pentagonal numbers, Pj and Pk, for which their sum and difference are pentagonal
and D = |Pk − Pj| is minimised; what is the value of D?
Answer: 5482660
"""


def pentagonal(n: int) -> int:
    return n * (3 * n - 1) // 2


def is_pentagonal(p: int):
    return (1 + 24 * p) ** 0.5 % 6 == 5.0


def solution() -> int:
    i = 0
    while i := i + 1:
        for j in range(i - 1, 0, -1):
            pi, pj = pentagonal(i), pentagonal(j)
            if is_pentagonal(pi - pj) and is_pentagonal(pi + pj):
                return pi - pj


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(solution)(answer=5482660)