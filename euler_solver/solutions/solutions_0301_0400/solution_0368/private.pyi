#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 368: A Kempner-like Series.

Problem Statement:
    The harmonic series 1 + 1/2 + 1/3 + 1/4 + ... is well known to be divergent.

    If we however omit from this series every term where the denominator has a 9 in
    it, the series remarkably enough converges to approximately 22.9206766193. This
    modified harmonic series is called the Kempner series.

    Let us now consider another modified harmonic series by omitting from the
    harmonic series every term where the denominator has 3 or more equal
    consecutive digits. One can verify that out of the first 1200 terms of the
    harmonic series, only 20 terms will be omitted. These 20 omitted terms are:
    1/111, 1/222, 1/333, 1/444, 1/555, 1/666, 1/777, 1/888, 1/999, 1/1000,
    1/1110, 1/1111, 1/1112, 1/1113, 1/1114, 1/1115, 1/1116, 1/1117, 1/1118,
    1/1119.

    This series converges as well.

    Find the value the series converges to.
    Give your answer rounded to 10 digits behind the decimal point.

Solution Approach:
    Build a digit-DP automaton accepting base-10 integers that do not contain any
    run of three or more equal consecutive digits (state tracks last digit/run).
    Enumerate allowed prefixes; all numbers with a fixed prefix form an integer
    interval. Compute the sum of reciprocals over an interval via H(b)-H(a-1)
    using high-precision arithmetic or series acceleration to the required digits.
    Truncate when the remaining tail is provably below 10^-11 to guarantee 10
    decimal places. Complexity scales with the number of prefixes needed for
    the precision; memory is small (states times branching).

Answer: ...
URL: https://projecteuler.net/problem=368
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 368
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_a_kempner_like_series_p0368_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))