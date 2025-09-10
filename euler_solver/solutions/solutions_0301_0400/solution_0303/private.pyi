#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 303: Multiples with Small Digits.

Problem Statement:
    For a positive integer n, define f(n) as the least positive multiple of n
    that, written in base 10, uses only digits <= 2.

    Thus f(2) = 2, f(3) = 12, f(7) = 21, f(42) = 210, f(89) = 1121222.

    Also, sum_{n = 1}^{100} f(n)/n = 11363107.

    Find sum_{n = 1}^{10000} f(n)/n.

Solution Approach:
    For each n, find the smallest base-10 number composed only of digits 0,1,2
    that is divisible by n. Model states as remainders mod n and perform a
    BFS on transitions that append digits {0,1,2}, starting with 1 and 2
    to avoid leading zeros. Track parent/remainder to reconstruct f(n) when
    remainder 0 is reached. This yields O(n) states and O(1) work per state,
    so roughly O(n) time per n; naive total is about O(N^2) for N=10000.
    Use integer arithmetic and modular congruences; sum f(n)/n accumulates in
    Python's bigint. Memory is O(n) per BFS; consider reusing structures.

Answer: ...
URL: https://projecteuler.net/problem=303
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 303
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 10000}},
    {'category': 'extra', 'input': {'max_limit': 20000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_multiples_with_small_digits_p0303_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))