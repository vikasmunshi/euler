#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 634: Numbers of the Form a^2b^3.

Problem Statement:
    Define F(n) to be the number of integers x ≤ n that can be written in the form
    x = a^2 b^3, where a and b are integers not necessarily different and both greater
    than 1.

    For example, 32 = 2^2 × 2^3 and 72 = 3^2 × 2^3 are the only two integers less than 100
    that can be written in this form. Hence, F(100) = 2.

    Further you are given F(2 × 10^4) = 130 and F(3 × 10^6) = 2014.

    Find F(9 × 10^18).

URL: https://projecteuler.net/problem=634
"""
from typing import Any

euler_problem: int = 634
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 9000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'VcVZzcJwonE1TJO4wePip9FxRjfWTeWk1dB3Jw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
