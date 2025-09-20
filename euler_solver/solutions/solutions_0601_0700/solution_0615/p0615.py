#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 615: The Millionth Number with at Least One Million Prime Factors.

Problem Statement:
    Consider the natural numbers having at least 5 prime factors, which don't have to be distinct.
    Sorting these numbers by size gives a list which starts with:
        32 = 2 · 2 · 2 · 2 · 2
        48 = 2 · 2 · 2 · 2 · 3
        64 = 2 · 2 · 2 · 2 · 2 · 2
        72 = 2 · 2 · 2 · 3 · 3
        80 = 2 · 2 · 2 · 2 · 5
        96 = 2 · 2 · 2 · 2 · 2 · 3
        ...
    So, for example, the fifth number with at least 5 prime factors is 80.

    Find the millionth number with at least one million prime factors.
    Give your answer modulo 123454321.

URL: https://projecteuler.net/problem=615
"""
from typing import Any

euler_problem: int = 615
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'k': 5, 'modulo': 123454321}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000, 'k': 1000000, 'modulo': 123454321}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
