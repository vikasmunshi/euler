#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 752: Powers of 1+√7.

Problem Statement:
    When (1+√7) is raised to an integral power, n, we always get a number of the
    form (a+b√7).
    We write (1+√7)^n = α(n) + β(n)√7.

    For a given number x we define g(x) to be the smallest positive integer n such that:
        α(n) ≡ 1 (mod x) and β(n) ≡ 0 (mod x),
    and g(x) = 0 if there is no such value of n. For example, g(3) = 0, g(5) = 12.

    Further define
        G(N) = sum of g(x) for x = 2 to N.
    You are given G(10^2) = 28891 and G(10^3) = 13131583.

    Find G(10^6).

URL: https://projecteuler.net/problem=752
"""
from typing import Any

euler_problem: int = 752
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'IeYUzOUiPZB4t/Or'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
