#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 26: Reciprocal Cycles.

Problem Statement:
    A unit fraction contains 1 in the numerator. The decimal representation of
    the unit fractions with denominators 2 to 10 are given:
        1/2 = 0.5
        1/3 = 0.(3)
        1/4 = 0.25
        1/5 = 0.2
        1/6 = 0.1(6)
        1/7 = 0.(142857)
        1/8 = 0.125
        1/9 = 0.(1)
        1/10 = 0.1
    Where 0.1(6) means 0.166666..., and has a 1-digit recurring cycle. It can
    be seen that 1/7 has a 6-digit recurring cycle.

    Find the value of d < 1000 for which 1/d contains the longest recurring
    cycle in its decimal fraction part.

Solution Approach:
    Apply number theory observing that the length of the recurring cycle of
    1/d is the order of 10 modulo d. Use modular arithmetic to find the cycle
    length efficiently for each d. Compare and track the maximum length.
    Time complexity: O(N^2) worst, but efficient for N=1000.

Answer: 983
URL: https://projecteuler.net/problem=26
"""
from __future__ import annotations

from math import gcd
from typing import Any, Optional

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 26
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'limit': 10}, 'answer': 7},
    {'category': 'main', 'input': {'limit': 1000}, 'answer': 983},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_reciprocal_cycles_p0026_s0(*, limit: int) -> int:
    return max(((multiplicative_order(a=10, modulus=d), d) for i in range(max(limit // 10, 10)) if
                (d := (limit - i)) > 6 and gcd(d, 10) == 1))[1]


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
