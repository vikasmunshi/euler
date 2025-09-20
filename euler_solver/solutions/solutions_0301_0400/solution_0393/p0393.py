#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 393: Migrating Ants.

Problem Statement:
    An n x n grid of squares contains n^2 ants, one ant per square.
    All ants decide to move simultaneously to an adjacent square (usually 4
    possibilities, except for ants on the edge of the grid or at the corners).
    We define f(n) to be the number of ways this can happen without any ants
    ending on the same square and without any two ants crossing the same edge
    between two squares.

    You are given that f(4) = 88.
    Find f(10).

URL: https://projecteuler.net/problem=393
"""
from typing import Any

euler_problem: int = 393
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 10}, 'answer': None},
    {'category': 'extra', 'input': {'n': 12}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
