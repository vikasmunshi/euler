#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 245: Coresilience.

Problem Statement:
    We shall call a fraction that cannot be cancelled down a resilient fraction.
    Furthermore we shall define the resilience of a denominator, R(d), to be the
    ratio of its proper fractions that are resilient; for example, R(12) = 4/11.

    The resilience of a number d > 1 is then phi(d)/(d - 1), where phi is Euler's
    totient function.

    We further define the coresilience of a number n > 1 as
    C(n) = (n - phi(n)) / (n - 1).

    The coresilience of a prime p is C(p) = 1/(p - 1).

    Find the sum of all composite integers 1 < n <= 2*10^11 for which C(n) is a
    unit fraction (a fraction with numerator 1).

URL: https://projecteuler.net/problem=245
"""
from typing import Any

euler_problem: int = 245
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 200000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
