#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 807: Loops of Ropes.

Problem Statement:
    Given a circle C and an integer n > 1, we perform the following operations.

    In step 0, we choose two uniformly random points R_0 and B_0 on C.
    In step i (1 <= i < n), we first choose a uniformly random point R_i on C and
    connect the points R_{i - 1} and R_i with a red rope; then choose a uniformly
    random point B_i on C and connect the points B_{i - 1} and B_i with a blue rope.
    In step n, we first connect the points R_{n - 1} and R_0 with a red rope; then
    connect the points B_{n - 1} and B_0 with a blue rope.
    Each rope is straight between its two end points, and lies above all previous ropes.

    After step n, we get a loop of red ropes, and a loop of blue ropes.
    Sometimes the two loops can be separated; sometimes they are "linked" and cannot
    be separated.

    Let P(n) be the probability that the two loops can be separated.
    For example, P(3) = 11/20 and P(5) ≈ 0.4304177690.

    Find P(80), rounded to 10 digits after decimal point.

URL: https://projecteuler.net/problem=807
"""
from typing import Any

euler_problem: int = 807
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 80}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
