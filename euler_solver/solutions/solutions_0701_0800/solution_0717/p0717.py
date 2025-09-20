#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 717: Summation of a Modular Formula.

Problem Statement:
    For an odd prime p, define f(p) = floor(2^(2^p) / p) modulo 2^p.
    For example, when p=3, floor(2^8 / 3) = 85 ≡ 5 mod 8, so f(3) = 5.

    Further define g(p) = f(p) modulo p. You are given g(31) = 17.

    Now define G(N) to be the summation of g(p) for all odd primes less than N.
    You are given G(100) = 474 and G(10^4) = 2819236.

    Find G(10^7).

URL: https://projecteuler.net/problem=717
"""
from typing import Any

euler_problem: int = 717
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
