#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 312: Cyclic Paths on Sierpiński Graphs.

Problem Statement:
    - A Sierpiński graph of order-1 (S1) is an equilateral triangle.
    - S_{n+1} is obtained from S_n by positioning three copies of S_n so that
      every pair of copies has one common corner.

    Let C(n) be the number of cycles that pass exactly once through all the
    vertices of S_n.

    For example, C(3) = 8 because eight such cycles can be drawn on S_3.

    It can also be verified that:
    C(1) = C(2) = 1
    C(5) = 71328803586048
    C(10000) mod 10^8 = 37652224
    C(10000) mod 13^8 = 617720485

    Find C(C(C(10000))) mod 13^8.

URL: https://projecteuler.net/problem=312
"""
from typing import Any

euler_problem: int = 312
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
