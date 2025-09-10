#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 383: Divisibility Comparison Between Factorials.

Problem Statement:
    Let f_5(n) be the largest integer x for which 5^x divides n.
    For example, f_5(625000) = 7.

    Let T_5(n) be the number of integers i which satisfy
    f_5((2 * i - 1)!) < 2 * f_5(i!) and 1 <= i <= n.
    It can be verified that T_5(10^3) = 68 and T_5(10^9) = 2408210.

    Find T_5(10^18).

Solution Approach:
    Use p-adic valuation / Legendre's formula: v_5(n!) = sum_{k>=1} floor(n / 5^k).
    Reduce the inequality f_5((2i-1)!) < 2*f_5(i!) to a condition on i involving sums
    of floor divisions by powers of 5. Count i up to N efficiently by digit-like
    analysis in base 5 or by a digit DP over the base-5 representation of i.
    Expect complexity around O(log_5 N) or O((log_5 N)^2) time and O(1) extra space.

Answer: ...
URL: https://projecteuler.net/problem=383
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 383
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_divisibility_comparison_between_factorials_p0383_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))