#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 156: Counting Digits.

Problem Statement:
    Starting from zero the natural numbers are written down in base 10 like this:
    0 1 2 3 4 5 6 7 8 9 10 11 12 ...
    Consider the digit d = 1. After we write down each number n, we update the
    total number of ones that have occurred and call this f(n,1). The first
    values for f(n,1) are:
    n  f(n,1)
    0  0
    1  1
    2  1
    3  1
    4  1
    5  1
    6  1
    7  1
    8  1
    9  1
    10 2
    11 4
    12 5
    Note that f(n,1) never equals 3. So the first two solutions of f(n,1)=n
    are n = 0 and n = 1. The next solution is n = 199981.
    In the same manner f(n,d) gives the total number of digits d that have been
    written down after the number n has been written. For every digit d != 0,
    0 is the first solution of f(n,d)=n.
    Let s(d) be the sum of all solutions for which f(n,d)=n. You are given that
    s(1)=22786974071.
    Find the sum s(d) for 1 <= d <= 9.
    Note: if, for some n, f(n,d)=n for more than one value of d this value of
    n is counted again for every value of d for which f(n,d)=n.

URL: https://projecteuler.net/problem=156
"""
from typing import Any

euler_problem: int = 156
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
