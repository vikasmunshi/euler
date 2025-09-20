#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 945: XOR-Equation C.

Problem Statement:
    We use x⊕y for the bitwise XOR of x and y.
    Define the XOR-product of x and y, denoted by x ⊗ y, similar to a long multiplication
    in base 2, except that the intermediate results are XORed instead of the usual integer addition.

    For example, 7 ⊗ 3 = 9, or in base 2, 111_2 ⊗ 11_2 = 1001_2:
        111_2
      ⊗  11_2
      ------
        111_2
      ⊕ 111_2
      ------
       1001_2

    We consider the equation:
        (a ⊗ a) ⊕ (2 ⊗ a ⊗ b) ⊕ (b ⊗ b) = c ⊗ c

    For example, (a, b, c) = (1, 2, 1) is a solution to this equation, and so is (1, 8, 13).

    Let F(N) be the number of solutions to this equation satisfying 0 ≤ a ≤ b ≤ N.
    You are given F(10) = 21.

    Find F(10^7).

URL: https://projecteuler.net/problem=945
"""
from typing import Any

euler_problem: int = 945
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
