#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=48
The series, 1^1 + 2^2 + 3^3 + ... + 10^10 = 10405071317.

Find the last ten digits of the series, 1^1 + 2^2 + 3^3 + ... + 1000^1000.
Answer: 9110846700
"""


def solution(n: int) -> int:
    return sum(i ** i for i in range(1, n + 1)) % 10000000000


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(solution,
                                    answers={10: 405071317, 100: 9027641920, 1000: 9110846700, 10000: 6237204500})
