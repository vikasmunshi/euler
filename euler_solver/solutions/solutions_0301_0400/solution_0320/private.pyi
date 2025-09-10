#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 320: Factorials Divisible by a Huge Integer.

Problem Statement:
    Let N(i) be the smallest integer n such that n! is divisible by (i!)^1234567890.
    Let S(u) = sum N(i) for 10 <= i <= u.
    S(1000) = 614538266565663.
    Find S(1000000) mod 10^18.

Solution Approach:
    Use prime valuations (Legendre's formula) to express v_p(n!) and v_p(i!).
    For each i compute required exponents e_p = 1234567890 * v_p(i!).
    For a given prime p and target e, find minimal n with v_p(n!) >= e by binary search.
    N(i) is the maximum such minimal n over primes p <= i.
    Compute v_p(i!) incrementally by factoring each i to update counts; maintain primes by sieve.
    Sum N(i) for 10..u with results reduced modulo 10^18.
    Time complexity: about O(u * (cost to update factors + primes per i * log n)),
    implemented carefully to run for u = 1e6 within resource limits.

Answer: ...
URL: https://projecteuler.net/problem=320
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 320
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000000}},
    {'category': 'extra', 'input': {'max_limit': 2000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_factorials_divisible_by_a_huge_integer_p0320_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))