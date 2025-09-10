#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 207: Integer Partition Equations.

Problem Statement:
    For some positive integers k there exists an integer partition of the form
    4^t = 2^t + k, where 4^t, 2^t and k are all positive integers and t is a
    real number.
    The first two such partitions are 4^1 = 2^1 + 2 and
    4^{1.5849625...} = 2^{1.5849625...} + 6.
    Partitions where t is also an integer are called perfect.
    For any m >= 1 let P(m) be the proportion of such partitions that are
    perfect with k <= m. Thus P(6) = 1/2.
    In the following table some values of P(m) are listed:
    P(5) = 1/1
    P(10) = 1/2
    P(15) = 2/3
    P(20) = 1/2
    P(25) = 1/2
    P(30) = 2/5
    ...
    P(180) = 1/4
    P(185) = 3/13
    Find the smallest m for which P(m) < 1/12345.

Solution Approach:
    Observe x = 2^t satisfies x^2 - x - k = 0, so x = (1+sqrt(1+4k))/2.
    Perfect partitions occur when x is a power of two: x = 2^n, hence
    k_n = 2^n(2^n - 1). Count perfect k <= m as the largest n with k_n <= m.
    For m in [k_t, k_{t+1}-1] we have P(m) = t / m. Search increasing t and
    for each t find the minimal m >= k_t with t / m < 1/12345. Scan until the
    condition falls between consecutive k_t; complexity is O(number of t) =
    O(log m) and uses simple integer arithmetic.

Answer: ...
URL: https://projecteuler.net/problem=207
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 207
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'threshold_denom': 2}},
    {'category': 'main', 'input': {'threshold_denom': 12345}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_integer_partition_equations_p0207_s0(*, threshold_denom: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))