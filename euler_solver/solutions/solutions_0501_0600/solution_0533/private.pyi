#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 533: Minimum Values of the Carmichael Function.

Problem Statement:
    The Carmichael function λ(n) is defined as the smallest positive integer m such
    that a^m = 1 modulo n for all integers a coprime with n.
    For example λ(8) = 2 and λ(240) = 4.

    Define L(n) as the smallest positive integer m such that λ(k) ≥ n for all k ≥ m.
    For example, L(6) = 241 and L(100) = 20174525281.

    Find L(20,000,000). Give the last 9 digits of your answer.

Solution Approach:
    Use number theory involving the Carmichael function and its known properties.
    Analyze growth behavior and find the minimal m ensuring λ(k) ≥ n for k ≥ m.
    Efficiently compute or approximate L(n) for large n using prime factorization
    and properties of orders modulo n. Expect complexity dominated by prime handling.

Answer: ...
URL: https://projecteuler.net/problem=533
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 533
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 20000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_minimum_values_of_the_carmichael_function_p0533_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))