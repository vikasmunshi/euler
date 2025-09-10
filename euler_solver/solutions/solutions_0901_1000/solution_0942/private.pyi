#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 942: Mersenne's Square Root.

Problem Statement:
    Given a natural number q, let p = 2^q - 1 be the q-th Mersenne number.

    Let R(q) be the minimal square root of q modulo p, if one exists. In other words,
    R(q) is the smallest positive integer x such that x^2 - q is divisible by p.

    For example, R(5) = 6 and R(17) = 47569.

    Find R(74207281). Give your answer modulo 10^9 + 7.

    Note: 2^74207281 - 1 is prime.

Solution Approach:
    Use number theory and modular arithmetic related to finite fields modulo a large
    Mersenne prime. Apply efficient modular square root algorithms (e.g., Tonelli-Shanks)
    adapted for this prime. Use fast exponentiation for modulo operations and exploit
    properties of Mersenne primes. Expect complexity dominated by modular exponentiation.

Answer: ...
URL: https://projecteuler.net/problem=942
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 942
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'q': 5}},
    {'category': 'dev', 'input': {'q': 17}},
    {'category': 'main', 'input': {'q': 74207281}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_mersennes_square_root_p0942_s0(*, q: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))