#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 124: Ordered Radicals.

Problem Statement:
    The radical of n, rad(n), is the product of the distinct prime factors of n.
    For example, 504 = 2^3 * 3^2 * 7, so rad(504) = 2 * 3 * 7 = 42.

    If we calculate rad(n) for 1 <= n <= 10, then sort the integers by rad(n),
    and break ties by the value of n, we obtain a sorted sequence of n-values.
    Let E(k) be the k-th element in that sorted n column; for example E(4) = 8
    and E(6) = 9.

    If rad(n) is sorted for 1 <= n <= 100000, find E(10000).

Solution Approach:
    Compute rad(n) for all n up to max_limit using a sieve-like method:
    initialize rad[i]=1 and for each prime p multiply rad[multiples] by p.
    This runs in about O(n log log n) for the sieve and O(n log n) for the
    final sort of pairs (rad[n], n). Space is O(n). Return the k-th element
    after sorting with ties broken by n.

Answer: ...
URL: https://projecteuler.net/problem=124
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 124
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10, 'k': 4}},
    {'category': 'main', 'input': {'max_limit': 100000, 'k': 10000}},
    {'category': 'extra', 'input': {'max_limit': 200000, 'k': 20000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_ordered_radicals_p0124_s0(*, max_limit: int, k: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))