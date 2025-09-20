#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 774: Conjunctive Sequences.

Problem Statement:
    Let '&' denote the bitwise AND operation.
    For example, 10 & 12 = 1010_2 & 1100_2 = 1000_2 = 8.

    We shall call a finite sequence of non-negative integers (a_1, a_2, ..., a_n)
    conjunctive if a_i & a_{i+1} ≠ 0 for all i = 1 ... n-1.

    Define c(n,b) to be the number of conjunctive sequences of length n in which
    all terms are ≤ b.

    You are given that c(3,4) = 18, c(10,6) = 2496120, and c(100,200) ≡ 268159379
    (mod 998244353).

    Find c(123,123456789). Give your answer modulo 998244353.

URL: https://projecteuler.net/problem=774
"""
from typing import Any

euler_problem: int = 774
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 123, 'b': 123456789}, 'answer': None},
]
encrypted: str = (
    '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'
    'H9MHAlUo2mM5H+CD'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
