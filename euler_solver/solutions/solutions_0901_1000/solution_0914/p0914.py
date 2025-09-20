#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 914: Triangles inside Circles.

Problem Statement:
    For a given integer R consider all primitive Pythagorean triangles that can fit
    inside, without touching, a circle with radius R. Define F(R) to be the largest
    inradius of those triangles. You are given F(100) = 36.

    Find F(10^18).

URL: https://projecteuler.net/problem=914
"""
from typing import Any

euler_problem: int = 914
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'R': 100}, 'answer': None},
    {'category': 'main', 'input': {'R': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
