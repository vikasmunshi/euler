#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 188: Hyperexponentiation.

Problem Statement:
    The hyperexponentiation or tetration of a number a by a positive integer b,
    denoted by a ↑↑ b or ^b a, is recursively defined by:

    a ↑↑ 1 = a
    a ↑↑ (k+1) = a^(a ↑↑ k)

    Thus we have e.g. 3 ↑↑ 2 = 3^3 = 27, hence 3 ↑↑ 3 = 3^27 = 7625597484987.
    3 ↑↑ 4 is roughly 10^ (3.6383346400240996 × 10^12).

    Find the last 8 digits of 1777 ↑↑ 1855.

URL: https://projecteuler.net/problem=188
"""
from typing import Any

euler_problem: int = 188
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'base': 3, 'height': 3, 'mod_digits': 8}, 'answer': None},
    {'category': 'main', 'input': {'base': 1777, 'height': 1855, 'mod_digits': 8}, 'answer': None},
    {'category': 'extra', 'input': {'base': 2, 'height': 10000, 'mod_digits': 8}, 'answer': None},
]
encrypted: str = (
    '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'
    'WXxn+c79rSo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
