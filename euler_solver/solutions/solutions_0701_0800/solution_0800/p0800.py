#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 800: Hybrid Integers.

Problem Statement:
    An integer of the form p^q*q^p with prime numbers p != q is called a hybrid-integer.
    For example, 800 = 2^5 5^2 is a hybrid-integer.

    We define C(n) to be the number of hybrid-integers less than or equal to n.
    You are given C(800) = 2 and C(800^800) = 10790.

    Find C(800800^800800).

URL: https://projecteuler.net/problem=800
"""
from typing import Any

euler_problem: int = 800
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': '800'}, 'answer': None},
    {'category': 'dev', 'input': {'n': '800^800'}, 'answer': None},
    {'category': 'main', 'input': {'n': '800800^800800'}, 'answer': None},
]
encrypted: str = (
    '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'
    'HEfYZg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
