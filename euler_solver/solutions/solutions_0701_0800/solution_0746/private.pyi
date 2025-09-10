#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 746: A Messy Dinner.

Problem Statement:
    n families, each with four members, a father, a mother, a son and a daughter,
    were invited to a restaurant. They were all seated at a large circular table
    with 4n seats such that men and women alternate.

    Let M(n) be the number of ways the families can be seated such that none of
    the families were seated together. A family is considered to be seated
    together only when all the members of a family sit next to each other.

    For example, M(1)=0, M(2)=896, M(3)=890880 and M(10) ≡ 170717180 mod 1,000,000,007.

    Let S(n) = sum from k=2 to n of M(k).

    For example, S(10) ≡ 399291975 mod 1,000,000,007.

    Find S(2021). Give your answer modulo 1,000,000,007.

Solution Approach:
    Use combinatorics and inclusion-exclusion principle with careful consideration of
    circular seating and gender alternation constraints.
    Employ modular arithmetic to handle large numbers.
    Expected complexity involves factorial computations and combinatorial sums,
    possibly optimized by dynamic programming or precomputed factorial inverses.

Answer: ...
URL: https://projecteuler.net/problem=746
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 746
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}},
    {'category': 'main', 'input': {'max_n': 2021}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_a_messy_dinner_p0746_s0(*, max_n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))