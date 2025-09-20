#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 676: Matching Digit Sums.

Problem Statement:
    Let d(i,b) be the digit sum of the number i in base b. For example d(9,2)=2, since
    9=1001_2. When using different bases, the respective digit sums most of the time
    deviate from each other, for example d(9,4)=3 != d(9,2).

    However, for some numbers i there will be a match, like d(17,4)=d(17,2)=2.
    Let M(n,b1,b2) be the sum of all natural numbers i <= n for which d(i,b1)=d(i,b2).
    For example, M(10,8,2)=18, M(100,8,2)=292 and M(10^6,8,2)=19173952.

    Find the sum from k=3 to 6 of the sum from l=1 to k-2 of M(10^16, 2^k, 2^l),
    giving the last 16 digits as the answer.

URL: https://projecteuler.net/problem=676
"""
from typing import Any

euler_problem: int = 676
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000000000000000, 'k_range': (3, 6), 'l_relation': 'l < k - 1'},
     'answer': None},
]
encrypted: str = (
    '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'
    'gL1M+p3k5MGLoHwuSvdHXQeBPO4DXwN7'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
