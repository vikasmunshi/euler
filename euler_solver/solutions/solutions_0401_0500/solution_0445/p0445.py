#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 445: Retractions A.

Problem Statement:
    For every integer n > 1, the family of functions f_{n,a,b} is defined by
    f_{n,a,b}(x) ≡ a x + b mod n for a,b,x integer with 0 < a < n, 0 ≤ b < n, 0 ≤ x < n.

    We will call f_{n,a,b} a retraction if f_{n,a,b}(f_{n,a,b}(x)) ≡ f_{n,a,b}(x) mod n
    for every 0 ≤ x < n.

    Let R(n) be the number of retractions for n.

    It is given that the sum of R(binomial(100000, k)) for k from 1 to 99999 modulo
    1,000,000,007 is 628701600.

    Find the sum of R(binomial(10,000,000, k)) for k from 1 to 9,999,999 modulo 1,000,000,007.

URL: https://projecteuler.net/problem=445
"""
from typing import Any

euler_problem: int = 445
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
