#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 533: Minimum Values of the Carmichael Function.

Problem Statement:
    The Carmichael function λ(n) is defined as the smallest positive integer m such
    that a^m = 1 modulo n for all integers a coprime with n.
    For example λ(8) = 2 and λ(240) = 4.

    Define L(n) as the smallest positive integer m such that λ(k) ≥ n for all k ≥ m.
    For example, L(6) = 241 and L(100) = 20174525281.

    Find L(20,000,000). Give the last 9 digits of your answer.

URL: https://projecteuler.net/problem=533
"""
from typing import Any

euler_problem: int = 533
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 20000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
