#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 381: (prime-k) Factorial.

Problem Statement:
    For a prime p let S(p) = (sum (p-k)!) mod p for 1 <= k <= 5.

    For example, if p = 7,
    (7-1)! + (7-2)! + (7-3)! + (7-4)! + (7-5)!
    = 6! + 5! + 4! + 3! + 2!
    = 720 + 120 + 24 + 6 + 2 = 872.
    As 872 mod 7 = 4, S(7) = 4.

    It can be verified that sum S(p) = 480 for 5 <= p < 100.

    Find sum S(p) for 5 <= p < 10^8.

Solution Approach:
    Use Wilson's theorem to relate (p-k)! to inverses of small factorials modulo p.
    Observe (p-k)! ≡ (-1)^k * inv((k-1)!) (mod p) for p > k.
    S(p) becomes a small linear combination of inverses of fixed integers mod p.
    Generate primes up to the limit with a sieve, then for each prime compute these
    modular inverses (via pow or extended gcd) and sum S(p) modulo p. Complexity:
    sieve O(n log log n) time and O(n) space; per-prime inverse cost O(log p).
    Overall time ~ O(n log log n + pi(n) log p) in practice.

Answer: ...
URL: https://projecteuler.net/problem=381
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 381
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 100000000}},
    {'category': 'extra', 'input': {'max_limit': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_k_factorial_p0381_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))