#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 157: Base-10 Diophantine Reciprocal.

Problem Statement:
    Consider the diophantine equation 1/a + 1/b = p/10^n with a, b, p, n positive
    integers and a <= b.

    For n=1 this equation has 20 solutions that are listed below:
    1/1 + 1/1 = 20/10, 1/1 + 1/2 = 15/10, 1/1 + 1/5 = 12/10,
    1/1 + 1/10 = 11/10, 1/2 + 1/2 = 10/10
    1/2 + 1/5 = 7/10, 1/2 + 1/10 = 6/10, 1/3 + 1/6 = 5/10,
    1/3 + 1/15 = 4/10, 1/4 + 1/4 = 5/10
    1/4 + 1/20 = 3/10, 1/5 + 1/5 = 4/10, 1/5 + 1/10 = 3/10,
    1/6 + 1/30 = 2/10, 1/10 + 1/10 = 2/10
    1/11 + 1/110 = 1/10, 1/12 + 1/60 = 1/10, 1/14 + 1/35 = 1/10,
    1/15 + 1/30 = 1/10, 1/20 + 1/20 = 1/10

    How many solutions has this equation for 1 <= n <= 9?

Solution Approach:
    Multiply through and rearrange to obtain (p*a - 10^n)(p*b - 10^n) = 10^{2n}.
    Thus p*a - 10^n and p*b - 10^n are complementary divisors of 10^{2n}.
    Enumerate divisor pairs of 10^{2n} = 2^{2n} * 5^{2n} and reconstruct a,b,p
    checking integrality and a <= b. Use divisor arithmetic and gcd tests.
    Number of divisors is (2n+1)^2 so complexity is polynomial in n (feasible).
    Expected time: dominated by enumerating divisors, trivial for n <= 9.

Answer: ...
URL: https://projecteuler.net/problem=157
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 157
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 1}},
    {'category': 'main', 'input': {'max_n': 9}},
    {'category': 'extra', 'input': {'max_n': 12}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_base_10_diophantine_reciprocal_p0157_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))