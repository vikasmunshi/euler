#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 270: Cutting Squares.

Problem Statement:
    A square piece of paper with integer dimensions N x N is placed with a corner
    at the origin and two of its sides along the x- and y-axes. Then, we cut it
    up respecting the following rules:
    - We only make straight cuts between two points lying on different sides of
      the square, and having integer coordinates.
    - Two cuts cannot cross, but several cuts can meet at the same border point.
    - Proceed until no more legal cuts can be made.
    Counting any reflections or rotations as distinct, we call C(N) the number of
    ways to cut an N x N square. For example, C(1) = 2 and C(2) = 30.
    What is C(30) mod 10^8?

URL: https://projecteuler.net/problem=270
"""
from typing import Any

euler_problem: int = 270
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 30}, 'answer': None},
    {'category': 'extra', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    'S1UBdbEIerjlvBHr2EMWjw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
