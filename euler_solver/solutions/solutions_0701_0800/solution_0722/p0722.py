#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 722: Slowly Converging Series.

Problem Statement:
    For a non-negative integer k, define
    E_k(q) = sum from n=1 to infinity of sigma_k(n) * q^n
    where sigma_k(n) = sum of the k-th powers of the positive divisors of n.

    It can be shown that, for every k, the series E_k(q) converges for any 0 < q < 1.

    For example,
    E_1(1 - 1/2^4) = 3.872155809243e2
    E_3(1 - 1/2^8) = 2.767385314772e10
    E_7(1 - 1/2^15) = 6.725803486744e39
    All the above values are given in scientific notation rounded to twelve digits
    after the decimal point.

    Find the value of E_15(1 - 1/2^25).
    Give the answer in scientific notation rounded to twelve digits after the decimal point.

URL: https://projecteuler.net/problem=722
"""
from typing import Any

euler_problem: int = 722
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'fUdITCB5Y54lEJbj'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
