#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 305: Reflexive Position.

Problem Statement:
    Let's call S the (infinite) string that is made by concatenating the
    consecutive positive integers (starting from 1) written down in base 10.
    Thus, S = 1234567891011121314151617181920212223242...
    It's easy to see that any number will show up an infinite number of times
    in S.
    Let f(n) be the starting position of the n-th occurrence of n in S.
    For example, f(1)=1, f(5)=81, f(12)=271 and f(7780)=111111365.
    Find the sum of f(3^k) for 1 <= k <= 13.

URL: https://projecteuler.net/problem=305
"""
from typing import Any

euler_problem: int = 305
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_k': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_k': 13}, 'answer': None},
    {'category': 'extra', 'input': {'max_k': 16}, 'answer': None},
]
encrypted: str = (
    '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'
    'TPNzojnldaQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
