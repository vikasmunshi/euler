#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 801: x^y = y^x.

Problem Statement:
    The positive integral solutions of the equation x^y = y^x are (2,4), (4,2) and (k,k)
    for all k > 0.

    For a given positive integer n, let f(n) be the number of integral values 0 < x,y <= n^2 - n
    such that x^y ≡ y^x (mod n).

    For example, f(5) = 104 and f(97) = 1614336.

    Let S(M,N) = sum f(p) where the sum is taken over all primes p satisfying M <= p <= N.

    You are given S(1, 10^2) = 7381000 and S(1, 10^5) ≡ 701331986 (mod 993353399).

    Find S(10^16, 10^16 + 10^6). Give your answer modulo 993353399.

URL: https://projecteuler.net/problem=801
"""
from typing import Any

euler_problem: int = 801
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'rWh+mS6QJbegHJCCWgiVzaDQRY0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
