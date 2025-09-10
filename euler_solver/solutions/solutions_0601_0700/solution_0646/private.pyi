#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 646: Bounded Divisors.

Problem Statement:
    Let n be a natural number and p_1^{alpha_1} * p_2^{alpha_2} * ... * p_k^{alpha_k} its prime
    factorisation.
    Define the Liouville function lambda(n) as lambda(n) = (-1)^{sum of alpha_i}.
    (i.e. -1 if the sum of the exponents alpha_i is odd and 1 if the sum is even.)
    Let S(n, L, H) be the sum of lambda(d) * d over all divisors d of n for which L <= d <= H.

    You are given:
      S(10!, 100, 1000) = 1457
      S(15!, 10^3, 10^5) = -107974
      S(30!, 10^8, 10^{12}) = 9766732243224.

    Find S(70!, 10^{20}, 10^{60}) modulo 1000000007.

Solution Approach:
    Use prime factorization properties and divisor generation combined with the Liouville function.
    Efficiently enumerate divisors within bounds L and H using number theory and combinatorial sums.
    Employ modular arithmetic for large results.
    Advanced factorial prime decompositions and interval pruning essential for feasibility.
    Expected complexity involves careful combinatorial and arithmetic optimizations.

Answer: ...
URL: https://projecteuler.net/problem=646
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 646
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'L': 100, 'H': 1000}},
    {'category': 'main', 'input': {'n': 70, 'L': 10**20, 'H': 10**60}},
    {'category': 'extra', 'input': {'n': 30, 'L': 10**8, 'H': 10**12}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_bounded_divisors_p0646_s0(*, n: int, L: int, H: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
