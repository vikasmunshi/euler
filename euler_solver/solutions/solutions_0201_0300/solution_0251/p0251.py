#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 251: Cardano Triplets.

Problem Statement:
    A triplet of positive integers (a, b, c) is called a Cardano Triplet if it
    satisfies the condition:
    (a + b*sqrt(c))^(1/3) + (a - b*sqrt(c))^(1/3) = 1
    For example, (2, 1, 5) is a Cardano Triplet.
    There exist 149 Cardano Triplets for which a + b + c <= 1000.
    Find how many Cardano Triplets exist such that a + b + c <= 110000000.

URL: https://projecteuler.net/problem=251
"""
from typing import Any

euler_problem: int = 251
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 110000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
