#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 638: Weighted Lattice Paths.

Problem Statement:
    Let P_{a,b} denote a path in a a×b lattice grid with following properties:
    The path begins at (0,0) and ends at (a,b).
    The path consists only of unit moves upwards or to the right; that is the
    coordinates are increasing with every move.

    Denote A(P_{a,b}) to be the area under the path. For the example of a P_{4,3}
    path given below, the area equals 6.

    Define G(P_{a,b},k) = k^{A(P_{a,b})}. Let C(a,b,k) equal the sum of
    G(P_{a,b},k) over all valid paths in a a×b lattice grid.

    You are given that
    C(2,2,1) = 6
    C(2,2,2) = 35
    C(10,10,1) = 184756
    C(15,10,3) ≡ 880419838 mod 1000000007
    C(10000,10000,4) ≡ 395913804 mod 1000000007

    Calculate the sum from k=1 to 7 of C(10^k+k, 10^k+k, k). Give your answer
    modulo 1000000007.

URL: https://projecteuler.net/problem=638
"""
from typing import Any

euler_problem: int = 638
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
