#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 291: Panaitopol Primes.

Problem Statement:
    A prime number p is called a Panaitopol prime if p = (x^4 - y^4)/(x^3 + y^3)
    for some positive integers x and y.
    Find how many Panaitopol primes are less than 5*10^15.

Solution Approach:
    Generate candidate values p = (x^4 - y^4)/(x^3 + y^3) for integer pairs x>y>0,
    simplify algebraically to reduce search (cancel common factors where possible).
    Bound x by solving growth of the expression to not exceed max_limit.
    Test each candidate for primality using a fast deterministic method (Miller-Rabin
    with appropriate bases for 64-bit or larger), de-duplicate and count.
    Expected complexity depends on the chosen algebraic reductions; aim for far fewer
    than O(max_limit) checks by bounding x and y and pruning with divisibility rules.

Answer: ...
URL: https://projecteuler.net/problem=291
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 291
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 5000000000000000}},
    {'category': 'extra', 'input': {'max_limit': 50000000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_panaitopol_primes_p0291_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))