#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 677: Coloured Graphs.

Problem Statement:
    Let g(n) be the number of undirected graphs with n nodes satisfying the
    following properties:
        - The graph is connected and has no cycles or multiple edges.
        - Each node is either red, blue, or yellow.
        - A red node may have no more than 4 edges connected to it.
        - A blue or yellow node may have no more than 3 edges connected to it.
        - An edge may not directly connect a yellow node to a yellow node.

    For example, g(2)=5, g(3)=15, and g(4) = 57.
    You are also given that g(10) = 710249 and g(100) ≡ 919747298 (mod 1,000,000,007).

    Find g(10,000) mod 1,000,000,007.

URL: https://projecteuler.net/problem=677
"""
from typing import Any

euler_problem: int = 677
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    'YKVgr2Wpo5U='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
