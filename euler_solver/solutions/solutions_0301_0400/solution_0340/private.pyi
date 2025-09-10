#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 340: Crazy Function.

Problem Statement:
    For fixed integers a, b, c, define the crazy function F(n) as follows:
    F(n) = n - c for all n > b
    F(n) = F(a + F(a + F(a + F(a + n)))) for all n <= b

    Also, define S(a, b, c) = sum_{n = 0}^b F(n).

    For example, if a = 50, b = 2000 and c = 40, then F(0) = 3240 and F(2000)
    = 2040. Also, S(50, 2000, 40) = 5204240.

    Find the last 9 digits of S(21^7, 7^21, 12^7).

Solution Approach:
    Model the definition as functional iteration with a base case for n > b and
    a 4-fold nested composition for n <= b. Use memoization to compute F(n)
    for n in [0, b] while tracking values that exceed b to apply the base rule.
    Detect cycles in the functional graph to avoid repeated work and compute
    contributions to the sum efficiently. Use arithmetic modulo 10^9 to get
    the last 9 digits. Expected complexity: roughly O(b) time and O(b) memory
    with careful cycle handling and memoization.

Answer: ...
URL: https://projecteuler.net/problem=340
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 340
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 50, 'b': 2000, 'c': 40}},
    {'category': 'main', 'input': {'a': 1801088541, 'b': 558545864083284007, 'c': 35831808}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_crazy_function_p0340_s0(*, a: int, b: int, c: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))