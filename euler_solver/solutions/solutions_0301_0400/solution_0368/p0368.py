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

URL: https://projecteuler.net/problem=368
"""
from typing import Any

euler_problem: int = 368
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'x66JHcy4ccvL3EWuR+Ms0POxvI4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
