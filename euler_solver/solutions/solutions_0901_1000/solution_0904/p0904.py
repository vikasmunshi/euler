#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 904: Pythagorean Angle.

Problem Statement:
    Given a right-angled triangle with integer sides, the smaller angle formed by the
    two medians drawn on the the two perpendicular sides is denoted by θ.

    Let f(α, L) denote the sum of the sides of the right-angled triangle minimizing
    the absolute difference between θ and α among all right-angled triangles with
    integer sides and hypotenuse not exceeding L.
    If more than one triangle attains the minimum value, the triangle with the maximum
    area is chosen. All angles in this problem are measured in degrees.

    For example, f(30,10^2)=198 and f(10,10^6)=1600158.

    Define F(N,L)=∑_(n=1)^N f(³√n, L).
    You are given F(10,10^6)=16684370.

    Find F(45000, 10^10).

URL: https://projecteuler.net/problem=904
"""
from typing import Any

euler_problem: int = 904
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10, 'L': 1000000}, 'answer': None},
    {'category': 'main', 'input': {'N': 45000, 'L': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Zuc08w=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
