#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 183: Maximum Product of Parts.

Problem Statement:
    Let N be a positive integer and let N be split into k equal parts, r = N/k,
    so that N = r + r + ... + r.
    Let P be the product of these parts, P = r * r * ... * r = r^k.

    For example, if 11 is split into five equal parts, 11 = 2.2 + 2.2 + 2.2 + 2.2
    + 2.2, then P = 2.2^5 = 51.53632.

    Let M(N) = P_max for a given value of N.

    It turns out that the maximum for N = 11 is found by splitting eleven into
    four equal parts which leads to P_max = (11/4)^4; that is, M(11) = 14641/256
    = 57.19140625, which is a terminating decimal.

    However, for N = 8 the maximum is achieved by splitting it into three equal
    parts, so M(8) = 512/27, which is a non-terminating decimal.

    Let D(N) = N if M(N) is a non-terminating decimal and D(N) = -N if M(N)
    is a terminating decimal.

    For example, sum_{N = 5}^{100} D(N) is 2438.

    Find sum_{N = 5}^{10000} D(N).

Solution Approach:
    Use continuous optimization: maximize f(k) = (N/k)^k by maximizing k ln(N/k).
    The continuous optimum is near k = N / e, so test integer k around floor(N/e)
    (e.g., floor(N/e) and ceil(N/e)) to find the integer maximizer.

    For the terminating-decimal test, write r = N/k = a/b in lowest terms where
    b = k / gcd(N,k). Then M(N) = (a/b)^k has terminating decimal iff b has
    no prime factors other than 2 and 5.

    Iterate N from 5 to limit, pick the best k per N, test b's prime factors,
    and accumulate D(N). Complexity O(limit * log N) with small-factor checks.

Answer: ...
URL: https://projecteuler.net/problem=183
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 183
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_maximum_product_of_parts_p0183_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))