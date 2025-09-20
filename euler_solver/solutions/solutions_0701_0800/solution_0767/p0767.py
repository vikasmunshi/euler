#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 767: Window into a Matrix II.

Problem Statement:
    A window into a matrix is a contiguous sub matrix.

    Consider a 16×n matrix where every entry is either 0 or 1.
    Let B(k,n) be the total number of these matrices such that the sum of the entries
    in every 2×k window is k.

    You are given that B(2,4) = 65550 and B(3,9) ≡ 87273560 modulo 1,000,000,007.

    Find B(10^5,10^16). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=767
"""
from typing import Any

euler_problem: int = 767
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 2, 'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'k': 100000, 'n': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
