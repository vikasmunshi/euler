#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 356: Largest Roots of Cubic Polynomials.

Problem Statement:
    Let a_n be the largest real root of a polynomial g(x) = x^3 - 2^n * x^2 + n.
    For example, a_2 = 3.86619826...
    Find the last eight digits of the sum for i = 1 to 30 of floor(a_i^987654321).
    Note: floor(a) represents the floor function.

Solution Approach:
    For each n compute the largest real root a_n of x^3 - 2^n*x^2 + n using a robust
    numerical root finder (bisection or Newton with safe bracketing) to high precision.
    Compute floor(a_n^987654321) and accumulate the sum modulo 10^8. Use careful
    floating-point or fixed-point arithmetic to get the integer part of huge powers.
    Total work is O(N * iterations * cost_eval) with modest memory; N = 30 for main case.

Answer: ...
URL: https://projecteuler.net/problem=356
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 356
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}},
    {'category': 'main', 'input': {'max_n': 30}},
    {'category': 'extra', 'input': {'max_n': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_largest_roots_of_cubic_polynomials_p0356_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))