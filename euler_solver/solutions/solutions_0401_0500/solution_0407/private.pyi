#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 407: Idempotents.

Problem Statement:
    If we calculate a^2 mod 6 for 0 <= a <= 5 we get: 0, 1, 4, 3, 4, 1.
    The largest value of a such that a^2 ≡ a (mod 6) is 4.
    Let M(n) be the largest value of a < n such that a^2 ≡ a (mod n).
    So M(6) = 4.

    Find the sum of M(n) for 1 <= n <= 10^7.

Solution Approach:
    Use number theory and modular arithmetic to find idempotents modulo n.
    Utilize properties of the Chinese Remainder Theorem and factorization.
    Compute M(n) efficiently by analyzing factors and their contributions.
    Use sieves and prime factorization preprocessing for O(n log n) complexity.

Answer: ...
URL: https://projecteuler.net/problem=407
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 407
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_idempotents_p0407_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))