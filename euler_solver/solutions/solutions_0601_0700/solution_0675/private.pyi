#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 675: 2^{ω(n)}.

Problem Statement:
    Let ω(n) denote the number of distinct prime divisors of a positive integer n.
    So ω(1) = 0 and ω(360) = ω(2^3 × 3^2 × 5) = 3.

    Let S(n) be the sum of 2^{ω(d)} over all divisors d of n.
    E.g. S(6) = 2^{ω(1)} + 2^{ω(2)} + 2^{ω(3)} + 2^{ω(6)} = 2^0 + 2^1 + 2^1 + 2^2 = 9.

    Let F(n) = sum from i=2 to n of S(i!).
    F(10) = 4821.

    Find F(10,000,000). Give your answer modulo 1,000,000,087.

Solution Approach:
    Use multiplicative number theory properties of the function ω(n).
    Factorization of factorials and divisor sums involve prime counting.
    Use efficient prime sieves and prime counting techniques.
    Precompute needed primes and use fast modular arithmetic.
    Complexity involves prime counting and factorial divisor structure.

Answer: ...
URL: https://projecteuler.net/problem=675
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 675
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 10}},
    {'category': 'main', 'input': {'max_n': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_2_omega_n_p0675_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))