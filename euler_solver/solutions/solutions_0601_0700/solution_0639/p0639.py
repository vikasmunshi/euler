#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 639: Summing a Multiplicative Function.

Problem Statement:
    A multiplicative function f(x) is a function over positive integers satisfying
    f(1)=1 and f(a b)=f(a) f(b) for any two coprime positive integers a and b.

    For integer k let f_k(n) be a multiplicative function additionally satisfying
    f_k(p^e)=p^k for any prime p and any integer e>0.
    For example, f_1(2)=2, f_1(4)=2, f_1(18)=6 and f_2(18)=36.

    Let S_k(n)=∑_{i=1}^n f_k(i).
    For example, S_1(10)=41, S_1(100)=3512, S_2(100)=208090,
    S_1(10000)=35252550 and ∑_{k=1}^3 S_k(10^8) ≡ 338787512 mod 1,000,000,007.

    Find ∑_{k=1}^50 S_k(10^12) mod 1,000,000,007.

URL: https://projecteuler.net/problem=639
"""
from typing import Any

euler_problem: int = 639
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'zloJbpJHujvL9gNsOn23Tg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
