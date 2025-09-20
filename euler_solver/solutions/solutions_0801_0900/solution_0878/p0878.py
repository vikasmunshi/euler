#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 878: XOR-Equation B.

Problem Statement:
    We use x ⊕ y for the bitwise XOR of x and y.
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
        (a ⊗ a) ⊕ (2 ⊗ a ⊗ b) ⊕ (b ⊗ b) = k.

    For example, (a, b) = (3, 6) is a solution to this equation for k = 5.

    Let G(N,m) be the number of solutions to those equations with k ≤ m and
    0 ≤ a ≤ b ≤ N.

    You are given G(1000,100) = 398.

    Find G(10^17,1,000,000).

URL: https://projecteuler.net/problem=878
"""
from typing import Any

euler_problem: int = 878
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit_n': 1000, 'max_limit_m': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit_n': 100000000000000000, 'max_limit_m': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/LM+X9xevVY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
