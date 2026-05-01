#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 190: Maximising a Weighted Product.

Problem Statement:
    Let S_m = (x_1, x_2, ..., x_m) be the m-tuple of positive real numbers
    with x_1 + x_2 + ... + x_m = m for which P_m = x_1 * x_2^2 * ... * x_m^m
    is maximised.

    For example, it can be verified that floor(P_10) = 4112 (floor is the integer
    part function).

    Find sum_{m = 2}^{15} floor(P_m).

URL: https://projecteuler.net/problem=190
"""
from typing import Any

euler_problem: int = 190
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
