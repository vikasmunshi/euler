#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 703: Circular Logic II.

Problem Statement:
    Given an integer n, n ≥ 3, let B={false,true} and let B^n be the set of
    sequences of n values from B. The function f from B^n to B^n is defined by
    f(b_1 ... b_n) = c_1 ... c_n where:
        c_i = b_{i+1} for 1 ≤ i < n.
        c_n = b_1 AND (b_2 XOR b_3), where AND and XOR are the logical AND and
        exclusive OR operations.

    Let S(n) be the number of functions T from B^n to B such that for all x
    in B^n, T(x) AND T(f(x)) = false.
    You are given that S(3) = 35 and S(4) = 2118.

    Find S(20). Give your answer modulo 1001001011.

URL: https://projecteuler.net/problem=703
"""
from typing import Any

euler_problem: int = 703
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
