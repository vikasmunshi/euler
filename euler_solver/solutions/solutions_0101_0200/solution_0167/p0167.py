#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 167: Investigating Ulam Sequences.

Problem Statement:
    For two positive integers a and b, the Ulam sequence U(a,b) is defined by
    U(a,b)_1 = a, U(a,b)_2 = b and for k > 2, U(a,b)_k is the smallest integer
    greater than U(a,b)_{k - 1} which can be written in exactly one way as the
    sum of two distinct previous members of U(a,b).

    For example, the sequence U(1,2) begins with
    1, 2, 3 = 1 + 2, 4 = 1 + 3, 6 = 2 + 4, 8 = 2 + 6, 11 = 3 + 8;
    5 does not belong to it because 5 = 1 + 4 = 2 + 3 has two representations
    as the sum of two previous members, likewise 7 = 1 + 6 = 3 + 4.

    Find sum_{n = 2}^{10} U(2,2n+1)_k, where k = 10^11.

URL: https://projecteuler.net/problem=167
"""
from typing import Any

euler_problem: int = 167
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10, 'n_start': 2, 'n_end': 4}, 'answer': None},
    {'category': 'main', 'input': {'k': 100000000000, 'n_start': 2, 'n_end': 10}, 'answer': None},
    {'category': 'extra', 'input': {'k': 1000000, 'n_start': 2, 'n_end': 10}, 'answer': None},
]
encrypted: str = (
    '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'
    'u6MOPdD3M+hkrgXBNafUhFpnMFw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
