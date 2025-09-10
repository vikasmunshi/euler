#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 952: Order Modulo Factorial.

Problem Statement:
    Given a prime p and a positive integer n < p, let R(p, n) be the multiplicative order
    of p modulo n!.

    In other words, R(p, n) is the minimal positive integer r such that

        p^r ≡ 1 (mod n!)

    For example, R(7, 4) = 2 and R(10^9 + 7, 12) = 17280.

    Find R(10^9 + 7, 10^7). Give your answer modulo 10^9 + 7.

Solution Approach:
    Use number theory focusing on multiplicative orders modulo factorials.
    Factorials contain prime powers; use prime factorization to analyze modular
    constraints. Combine via least common multiple (LCM) over moduli. Employ
    group theory and modular arithmetic properties for the large prime modulus.
    Efficient prime factorization and order computation techniques are crucial.
    Expect complexity dominated by prime factorization and modular exponentiation.

Answer: ...
URL: https://projecteuler.net/problem=952
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 952
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 7, 'n': 4}},
    {'category': 'main', 'input': {'p': 1000000007, 'n': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_order_modulo_factorial_p0952_s0(*, p: int, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))