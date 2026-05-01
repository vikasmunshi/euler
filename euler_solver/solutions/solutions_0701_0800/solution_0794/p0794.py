#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 794: Seventeen Points.

Problem Statement:
    This problem uses half open interval notation where [a,b) represents a ≤ x < b.

    A real number, x_1, is chosen in the interval [0,1).
    A second real number, x_2, is chosen such that each of [0,1/2) and [1/2,1) contains
    exactly one of (x_1, x_2).
    Continue such that on the n-th step a real number, x_n, is chosen so that each of the
    intervals [(k-1)/n, k/n) for k in {1, ..., n} contains exactly one of
    (x_1, x_2, ..., x_n).

    Define F(n) to be the minimal value of the sum x_1 + x_2 + ... + x_n of a tuple
    (x_1, x_2, ..., x_n) chosen by such a procedure. For example, F(4) = 1.5 obtained
    with (x_1, x_2, x_3, x_4) = (0, 0.75, 0.5, 0.25).

    Surprisingly, no more than 17 points can be chosen by this procedure.

    Find F(17) and give your answer rounded to 12 decimal places.

URL: https://projecteuler.net/problem=794
"""
from typing import Any

euler_problem: int = 794
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
