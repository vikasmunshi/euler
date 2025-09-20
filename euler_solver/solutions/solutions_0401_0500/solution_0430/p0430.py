#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 430: Range Flips.

Problem Statement:
    N disks are placed in a row, indexed 1 to N from left to right.
    Each disk has a black side and white side. Initially all disks show their white side.

    At each turn, two, not necessarily distinct, integers A and B between 1 and N (inclusive)
    are chosen uniformly at random.
    All disks with an index from A to B (inclusive) are flipped.

    The following example shows the case N = 8. At the first turn A = 5 and B = 2, and at the
    second turn A = 4 and B = 6.

    Let E(N, M) be the expected number of disks that show their white side after M turns.
    We can verify that E(3, 1) = 10/9, E(3, 2) = 5/3, E(10, 4) ≈ 5.157 and E(100, 10) ≈ 51.893.

    Find E(10^10, 4000).
    Give your answer rounded to 2 decimal places behind the decimal point.

URL: https://projecteuler.net/problem=430
"""
from typing import Any

euler_problem: int = 430
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'm': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000, 'm': 4000}, 'answer': None},
]
encrypted: str = (
    '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'
    'zK9ACZeAZ44tjJh7WOPEVD49mHEE7UKw'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
