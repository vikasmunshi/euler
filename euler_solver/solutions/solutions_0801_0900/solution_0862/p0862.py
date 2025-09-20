#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 862: Larger Digit Permutation.

Problem Statement:
    For a positive integer n define T(n) to be the number of strictly larger integers
    which can be formed by permuting the digits of n.

    Leading zeros are not allowed and so for n = 2302 the total list of permutations
    would be:
    2023, 2032, 2203, 2230, 2302, 2320, 3022, 3202, 3220
    giving T(2302) = 4.

    Further define S(k) to be the sum of T(n) for all k-digit numbers n. You are
    given S(3) = 1701.

    Find S(12).

URL: https://projecteuler.net/problem=862
"""
from typing import Any

euler_problem: int = 862
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'sS6cOuFb8QpxavHLS90f+wKInKk='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
