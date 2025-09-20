#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 354: Distances in a Bee's Honeycomb.

Problem Statement:
    Consider a honey bee's honeycomb where each cell is a perfect regular
    hexagon with side length 1.

    One particular cell is occupied by the queen bee.

    For a positive real number L, let B(L) count the cells with distance L
    from the queen bee cell (all distances are measured from centre to
    centre); you may assume that the honeycomb is large enough to
    accommodate for any distance we wish to consider.

    For example, B(sqrt(3)) = 6, B(sqrt(21)) = 12 and B(111111111) = 54.

    Find the number of L <= 5*10^11 such that B(L) = 450.

URL: https://projecteuler.net/problem=354
"""
from typing import Any

euler_problem: int = 354
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 500000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'qdE8XkaaB58gLxNkHXTdqx8dsUOa09yqMb3r1w=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
