#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 877: XOR-Equation A.

Problem Statement:
    We use x⊕y for the bitwise XOR of x and y.
    Define the XOR-product of x and y, denoted by x ⊗ y, similar to a long
    multiplication in base 2, except that the intermediate results are XORed
    instead of the usual integer addition.

    For example, 7 ⊗ 3 = 9, or in base 2, 111_2 ⊗ 11_2 = 1001_2:
        111_2
      ⊗  11_2
      --------
        111_2
      ⊕ 111_2
      --------
        1001_2

    We consider the equation:
        (a ⊗ a) ⊕ (2 ⊗ a ⊗ b) ⊕ (b ⊗ b) = 5

    For example, (a, b) = (3, 6) is a solution.

    Let X(N) be the XOR of the b values for all solutions to this equation
    satisfying 0 ≤ a ≤ b ≤ N.
    You are given X(10) = 5.

    Find X(10^18).

URL: https://projecteuler.net/problem=877
"""
from typing import Any

euler_problem: int = 877
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
