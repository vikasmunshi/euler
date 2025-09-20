#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 736: Paths to Equality.

Problem Statement:
    Define two functions on lattice points:

        r(x,y) = (x+1, 2y)
        s(x,y) = (2x, y+1)

    A path to equality of length n for a pair (a,b) is a sequence
    ((a_1, b_1), (a_2, b_2), ..., (a_n, b_n)), where:
        (a_1, b_1) = (a, b)
        For k > 1, (a_k, b_k) = r(a_{k-1}, b_{k-1}) or (a_k, b_k) = s(a_{k-1}, b_{k-1})
        a_k ≠ b_k for k < n
        a_n = b_n

    a_n = b_n is called the final value.

    Example:
        (45,90) →r (46,180) →s (92,181) →s (184,182) →s (368,183) →s (736,184) →r
        (737,368) →s (1474,369) →r (1475,738) →r (1476,1476)

    This is a path to equality for (45,90) of length 10 and final value 1476.
    There is no path to equality of (45,90) with smaller length.

    Find the unique path to equality for (45,90) with smallest odd length.
    Enter the final value as your answer.

URL: https://projecteuler.net/problem=736
"""
from typing import Any

euler_problem: int = 736
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a': 45, 'b': 90}, 'answer': None},
]
encrypted: str = (
    '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'
    '9jgThlJTHDqtMfN6FbLmzQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
