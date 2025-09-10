#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 446: Retractions B.

Problem Statement:
    For every integer n>1, the family of functions f_{n,a,b} is defined by
    f_{n,a,b}(x) ≡ a x + b mod n where a,b,x are integers and 0 < a < n, 0 ≤ b < n,
    0 ≤ x < n.

    We will call f_{n,a,b} a retraction if f_{n,a,b}(f_{n,a,b}(x)) ≡ f_{n,a,b}(x) mod n
    for every 0 ≤ x < n.
    Let R(n) be the number of retractions for n.

    F(N) = ∑_{n=1}^N R(n^4 + 4).
    F(1024) = 77532377300600.

    Find F(10^7).
    Give your answer modulo 1,000,000,007.

Solution Approach:
    Use number theory and modular arithmetic to analyze the retraction condition.
    Employ algebraic simplifications on the modular affine functions.
    Efficiently compute R(n) using factorization and properties of modulo functions.
    Use fast summation techniques and modulo arithmetic to handle large N.
    Complexity depends on efficient factorization and summation over N up to 10^7.

Answer: ...
URL: https://projecteuler.net/problem=446
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 446
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 10**7}},
    {'category': 'dev', 'input': {'N': 1024}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_retractions_b_p0446_s0(*, N: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))