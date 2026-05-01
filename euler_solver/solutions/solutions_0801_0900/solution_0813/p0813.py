#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 813: XOR-Powers.

Problem Statement:
    We use x⊕y to be the bitwise XOR of x and y.

    Define the XOR-product of x and y, denoted by x ⊗ y, similar to a long multiplication
    in base 2, except that the intermediate results are XORed instead of the usual integer
    addition.

    For example, 11 ⊗ 11 = 69, or in base 2, 1011_2 ⊗ 1011_2 = 1000101_2:

        1011_2
      ⊗ 1011_2
      --------
        1011_2
       1011_2
      ⊕ 1011_2
      --------
      1000101_2

    Further we define P(n) = 11^{⊗ n} = 11 ⊗ 11 ⊗ ... ⊗ 11 (n times). For example P(2) = 69.

    Find P(8^{12} * 12^{8}). Give your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=813
"""
from typing import Any

euler_problem: int = 813
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
