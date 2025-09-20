#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 64: Odd Period Square Roots.

Problem Statement:
    All square roots are periodic when written as continued fractions and can
    be written in the form:

        sqrt(N) = a0 + 1/(a1 + 1/(a2 + 1/(a3 + ...)))

    For example, consider sqrt(23):

        sqrt(23) = 4 + sqrt(23) - 4
                 = 4 + 1 / (1 + (sqrt(23) - 3)/7)

    Continuing the expansion:

        sqrt(23) = 4 + 1 / (1 + 1 / (3 + 1 / (1 + 1 / (8 + ...))))

    The process produces a repeating sequence of partial denominators:
    [4; (1,3,1,8)] indicating the block (1,3,1,8) repeats indefinitely.

    The first ten continued fraction representations of irrational square roots
    show periodic sequences with varying lengths.

    Exactly four continued fractions for N ≤ 13 have an odd period.

    How many continued fractions for N ≤ 10,000 have an odd period?

Solution Approach:
    Use number theory and continued fraction expansion for square roots.
    Compute period length of continued fraction expansions for nonsquare N.
    Count how many N ≤ max_limit have odd period lengths.
    Expected complexity O(N * sqrt(N)) is feasible with efficient implementation.

Answer: 1322
URL: https://projecteuler.net/problem=64
"""
from __future__ import annotations

from math import isqrt, sqrt
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 64
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 13}, 'answer': 4},
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': 1322},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_odd_period_square_roots_p0064_s0(*, max_limit: int) -> int:
    return sum((get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not sqrt(n).is_integer()))


def get_period_length(n: int) -> int:
    a0 = a = isqrt(n)
    d, m, p = (1, 0, [])
    while True:
        m = d * a - m
        d = (n - m ** 2) // d
        a = (a0 + m) // d
        if (m, d, a) in p:
            break
        p.append((m, d, a))
    return len(p)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
