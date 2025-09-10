#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 615: The Millionth Number with at Least One Million Prime Factors.

Problem Statement:
    Consider the natural numbers having at least 5 prime factors, which don't have to be distinct.
    Sorting these numbers by size gives a list which starts with:
        32 = 2 · 2 · 2 · 2 · 2
        48 = 2 · 2 · 2 · 2 · 3
        64 = 2 · 2 · 2 · 2 · 2 · 2
        72 = 2 · 2 · 2 · 3 · 3
        80 = 2 · 2 · 2 · 2 · 5
        96 = 2 · 2 · 2 · 2 · 2 · 3
        ...
    So, for example, the fifth number with at least 5 prime factors is 80.

    Find the millionth number with at least one million prime factors.
    Give your answer modulo 123454321.

Solution Approach:
    Use combinatorics and prime factorization counting.
    Employ efficient number factor counting and binary search on the number space.
    Use prime factor counting with multiplicities for large inputs.
    Modular arithmetic applies to the final answer.
    Expected complexity involves fast counting and search algorithms.

Answer: ...
URL: https://projecteuler.net/problem=615
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 615
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'k': 5, 'modulo': 123454321}},
    {'category': 'main', 'input': {'n': 1000000, 'k': 1000000, 'modulo': 123454321}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_millionth_number_with_at_least_one_million_prime_factors_p0615_s0(*, n: int, k: int, modulo: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))