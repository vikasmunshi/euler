#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 731: A Stoneham Number.

Problem Statement:
    A = sum for i=1 to infinity of 1 / (3^i * 10^(3^i)).

    Define A(n) to be the 10 decimal digits from the nth digit onward.
    For example, A(100) = 4938271604 and A(10^8) = 2584642393.

    Find A(10^16).

URL: https://projecteuler.net/problem=731
"""
from typing import Any

euler_problem: int = 731
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'sMO4xIUeqhw9sMGxy5DUTg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
