#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 734: A Bit of Prime.

Problem Statement:
    The logical-OR of two bits is 0 if both bits are 0, otherwise it is 1.
    The bitwise-OR of two positive integers performs a logical-OR operation
    on each pair of corresponding bits in the binary expansion of its inputs.

    For example, the bitwise-OR of 10 and 6 is 14 because
    10 = 1010_2, 6 = 0110_2 and 14 = 1110_2.

    Let T(n, k) be the number of k-tuples (x_1, x_2, ..., x_k) such that
        every x_i is a prime ≤ n
        the bitwise-OR of the tuple is a prime ≤ n

    For example, T(5, 2) = 5. The five 2-tuples are (2, 2), (2, 3),
    (3, 2), (3, 3) and (5, 5).

    You are given T(100, 3) = 3355 and T(1000, 10) ≡ 2071632 (mod 1,000,000,007).

    Find T(10^6, 999983). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=734
"""
from typing import Any

euler_problem: int = 734
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 1000000, 'k': 999983}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
