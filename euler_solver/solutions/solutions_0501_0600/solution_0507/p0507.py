#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 507: Shortest Lattice Vector.

Problem Statement:
    Let t_n be the tribonacci numbers defined as:
    t_0 = t_1 = 0;
    t_2 = 1;
    t_n = t_{n-1} + t_{n-2} + t_{n-3} for n ≥ 3
    and let r_n = t_n mod 10^7.

    For each pair of vectors V_n = (v_1, v_2, v_3) and W_n = (w_1, w_2, w_3) with
    v_1 = r_{12n-11} - r_{12n-10}, v_2 = r_{12n-9} + r_{12n-8}, v_3 = r_{12n-7} * r_{12n-6}
    and
    w_1 = r_{12n-5} - r_{12n-4}, w_2 = r_{12n-3} + r_{12n-2}, w_3 = r_{12n-1} * r_{12n},

    we define S(n) as the minimal value of the Manhattan length of the vector
    D = k * V_n + l * W_n measured as
    |k * v_1 + l * w_1| + |k * v_2 + l * w_2| + |k * v_3 + l * w_3|
    for any integers k and l with (k, l) ≠ (0, 0).

    The first vector pair is (-1, 3, 28), (-11, 125, 40826).
    It is given that S(1) = 32 and the sum of S(n) for n=1 to 10 is 130762273722.

    Find the sum of S(n) for n=1 to 20000000.

URL: https://projecteuler.net/problem=507
"""
from typing import Any

euler_problem: int = 507
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 20000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '75Xz+Th6fCTUYHE6'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
