#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 133: Repunit Nonfactors.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k; for example, R(6) = 111111.

    Let us consider repunits of the form R(10^n).

    Although R(10), R(100), or R(1000) are not divisible by 17, R(10000) is
    divisible by 17. Yet there is no value of n for which R(10^n) will divide
    by 19. In fact, it is remarkable that 11, 17, 41, and 73 are the only four
    primes below one-hundred that can be a factor of R(10^n).

    Find the sum of all the primes below one-hundred thousand that will never
    be a factor of R(10^n).

Solution Approach:
    Number theory: for prime p not dividing 10, R(k) ≡ 0 (mod p) iff 10^k ≡ 1 (mod p).
    Thus p divides some R(10^n) iff the multiplicative order ord_p(10) divides
    some power of 10. Equivalently ord_p(10) must have no prime factors other
    than 2 or 5.

    Algorithm: sieve primes up to limit, skip 2 and 5, compute ord_p(10) by
    reducing p-1 via its prime divisors (factor p-1 using precomputed primes),
    and test if ord's prime factors are subset of {2,5}. Sum primes that fail
    the test. Expected complexity: sieve O(L log log L) plus factor reductions
    for each prime (practical for L = 100000).

Answer: ...
URL: https://projecteuler.net/problem=133
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 133
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 100000}},
    {'category': 'extra', 'input': {'max_limit': 200000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_repunit_nonfactors_p0133_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))