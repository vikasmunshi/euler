#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 451: Modular Inverses.

Problem Statement:
    Consider the number 15.
    There are eight positive numbers less than 15 which are coprime to 15:
    1, 2, 4, 7, 8, 11, 13, 14.
    The modular inverses of these numbers modulo 15 are: 1, 8, 4, 13, 2, 11, 7, 14
    because
    1 * 1 mod 15 = 1
    2 * 8 = 16 mod 15 = 1
    4 * 4 = 16 mod 15 = 1
    7 * 13 = 91 mod 15 = 1
    11 * 11 = 121 mod 15 = 1
    14 * 14 = 196 mod 15 = 1

    Let I(n) be the largest positive number m smaller than n-1 such that the modular
    inverse of m modulo n equals m itself.
    So I(15) = 11.
    Also I(100) = 51 and I(7) = 1.

    Find the sum of I(n) for 3 ≤ n ≤ 2×10^7.

URL: https://projecteuler.net/problem=451
"""
from typing import Any

euler_problem: int = 451
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
