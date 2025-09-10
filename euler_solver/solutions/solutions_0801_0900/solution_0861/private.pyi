#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 861: Products of Bi-Unitary Divisors.

Problem Statement:
    A unitary divisor of a positive integer n is a divisor d of n such that
    gcd(d, n/d) = 1.

    A bi-unitary divisor of n is a divisor d for which 1 is the only unitary
    divisor of d that is also a unitary divisor of n/d.

    For example, 2 is a bi-unitary divisor of 8, because the unitary divisors
    of 2 are {1, 2}, and the unitary divisors of 8/2 are {1, 4}, with 1 being
    the only unitary divisor in common.

    The bi-unitary divisors of 240 are {1,2,3,5,6,8,10,15,16,24,30,40,48,80,120,240}.

    Let P(n) be the product of all bi-unitary divisors of n. Define Q_k(N) as
    the number of positive integers 1 < n <= N such that P(n) = n^k. For
    example, Q_2(10^2)=51 and Q_6(10^6)=6189.

    Find the sum from k=2 to 10 of Q_k(10^12).

Solution Approach:
    Use number theory focused on divisors and unitary divisor properties.
    Analyze prime factorization constraints to characterize bi-unitary divisors.
    Efficient enumeration or formula derivation for P(n) and conditions for P(n)=n^k.
    Employ sieve methods and fast prime factorization for large N.
    Expected complexity: optimized with advanced divisor function theory.

Answer: ...
URL: https://projecteuler.net/problem=861
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 861
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10**12}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_products_of_bi_unitary_divisors_p0861_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))