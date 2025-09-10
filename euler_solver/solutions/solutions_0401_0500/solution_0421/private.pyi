#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 421: Prime Factors of n^15+1.

Problem Statement:
    Numbers of the form n^15+1 are composite for every integer n > 1.
    For positive integers n and m let s(n,m) be defined as the sum of the
    distinct prime factors of n^15+1 not exceeding m.

    E.g. 2^15+1 = 3 x 3 x 11 x 331.
    So s(2,10) = 3 and s(2,1000) = 3+11+331 = 345.

    Also 10^15+1 = 7 x 11 x 13 x 211 x 241 x 2161 x 9091.
    So s(10,100) = 31 and s(10,1000) = 483.
    Find sum s(n,10^8) for 1 <= n <= 10^11.

Solution Approach:
    Factorization for n^15+1 utilizes number theory: algebraic factorization,
    prime factorization, and fast primality tests. Using properties of
    cyclotomic polynomials and advanced factorization algorithms is essential.
    Summation limits and large n require efficient sieving and numeric methods.
    A careful blend of combinatorics and computational number theory is needed,
    likely with complexity dependent on prime sieves and factorization heuristics.

Answer: ...
URL: https://projecteuler.net/problem=421
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 421
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_factors_of_n15_plus_1_p0421_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))