#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 733: Ascending Subsequences.

Problem Statement:
    Let a_i be the sequence defined by a_i=153^i mod 10,000,019 for i >= 1.
    The first terms of a_i are:
    153, 23409, 3581577, 7980255, 976697, 9434375, ...

    Consider the subsequences consisting of 4 terms in ascending order. For
    the part of the sequence shown above, these are:
    153, 23409, 3581577, 7980255
    153, 23409, 3581577, 9434375
    153, 23409, 7980255, 9434375
    153, 23409, 976697, 9434375
    153, 3581577, 7980255, 9434375
    23409, 3581577, 7980255, 9434375

    Define S(n) to be the sum of the terms for all such subsequences within the
    first n terms of a_i. Thus S(6)=94513710.
    You are given that S(100)=4465488724217.

    Find S(10^6) modulo 1,000,000,007.

URL: https://projecteuler.net/problem=733
"""
from typing import Any

euler_problem: int = 733
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/cEh3WNKMoJaqJ3EPjv35ZgFX58='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
