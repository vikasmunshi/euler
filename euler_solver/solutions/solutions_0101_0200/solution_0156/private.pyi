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

Solution Approach:
    Compute f(n,d) efficiently by positional digit counting: for each digit
    position derive occurrences from the higher, current and lower parts.
    For each digit d in 1..9 find all n with f(n,d)=n by locating roots of
    g(n)=f(n,d)-n. g is non-decreasing so search per magnitude using binary
    search or targeted scans over ranges of n. Time: O(9 * D * log N) roughly,
    where D is number of digit positions and N the search bound.

Answer: ...
URL: https://projecteuler.net/problem=156
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 156
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_digits_p0156_s0() -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))