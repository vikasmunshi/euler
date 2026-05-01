#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 508: Integers in Base i-1.

Problem Statement:
    Consider the Gaussian integer i-1. A base i-1 representation of a Gaussian integer
    a+bi is a finite sequence of digits d_{n - 1}d_{n - 2}... d_1 d_0 such that:
        a+bi = d_{n - 1}(i - 1)^{n - 1} + d_{n - 2}(i - 1)^{n - 2} + ... + d_1(i - 1) + d_0
        Each d_k is in {0,1}
        There are no leading zeroes, i.e. d_{n-1} ≠ 0, unless a+bi is 0 itself.

    Examples of base i-1 representations:
        11+24i -> 111010110001101
        24-11i -> 110010110011
        8+0i -> 111000000
        -5+0i -> 11001101
        0+0i -> 0

    Every Gaussian integer has a unique base i-1 representation.

    Define f(a + bi) as the number of 1s in the unique base i-1 representation of a + bi.
    For example, f(11+24i) = 9 and f(24-11i) = 7.

    Define B(L) as the sum of f(a + bi) for all integers a, b such that |a| ≤ L and |b| ≤ L.
    For example, B(500) = 10795060.

    Find B(10^15) mod 1,000,000,007.

URL: https://projecteuler.net/problem=508
"""
from typing import Any

euler_problem: int = 508
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
