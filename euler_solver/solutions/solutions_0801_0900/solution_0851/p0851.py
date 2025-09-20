#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 851: SOP and POS.

Problem Statement:
    Let n be a positive integer and let E_n be the set of n-tuples of strictly positive
    integers.

    For u = (u_1, ..., u_n) and v = (v_1, ..., v_n) two elements of E_n, we define:

        the Sum Of Products of u and v, denoted by <u, v>, as the sum of u_i * v_i for i from 1 to n;
        the Product Of Sums of u and v, denoted by u ⋆ v, as the product of (u_i + v_i) for i from 1 to n.

    Let R_n(M) be the sum of u ⋆ v over all ordered pairs (u, v) in E_n such that <u, v> = M.
    For example: R_1(10) = 36, R_2(100) = 1873044, R_2(100!) ≡ 446575636 mod 10^9 + 7.

    Find R_6(10000!). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=851
"""
from typing import Any

euler_problem: int = 851
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 6, 'factorial': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Mo3uCg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
