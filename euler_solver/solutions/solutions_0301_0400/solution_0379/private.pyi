#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 379: Least Common Multiple Count.

Problem Statement:
    Let f(n) be the number of couples (x, y) with x and y positive integers,
    x <= y and the least common multiple of x and y equal to n.

    Let g be the summatory function of f, i.e.:
    g(n) = sum f(i) for 1 <= i <= n.

    You are given that g(10^6) = 37429395.

    Find g(10^12).

Solution Approach:
    Use multiplicative-function properties. For n = prod p^e the number of
    ordered pairs (x, y) with lcm n equals prod_p (2*e_p + 1).

    Since f counts pairs with x <= y, f(n) = (prod_p (2*e_p + 1) + 1) / 2.

    Compute g(N) = sum_{n<=N} f(n) using fast summation techniques for
    multiplicative functions (Dirichlet convolution / hyperbola method) and
    sieving for primes and prime powers.

    With careful implementation this can be done in sublinear time, typically
    around O(N^{2/3}) time with O(N^{1/3}) memory heuristically.

Answer: ...
URL: https://projecteuler.net/problem=379
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 379
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000000000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_least_common_multiple_count_p0379_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))