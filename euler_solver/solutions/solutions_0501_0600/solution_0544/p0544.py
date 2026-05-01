#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 544: Chromatic Conundrum.

Problem Statement:
    Let F(r, c, n) be the number of ways to colour a rectangular grid with r rows and c
    columns using at most n colours such that no two adjacent cells share the same colour.
    Cells that are diagonal to each other are not considered adjacent.

    For example, F(2,2,3) = 18, F(2,2,20) = 130340, and F(3,4,6) = 102923670.

    Let S(r, c, n) = sum from k=1 to n of F(r, c, k).

    For example, S(4,4,15) mod 10^9+7 = 325951319.

    Find S(9,10,1112131415) mod 10^9+7.

URL: https://projecteuler.net/problem=544
"""
from typing import Any

euler_problem: int = 544
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'r': 2, 'c': 2, 'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'r': 9, 'c': 10, 'n': 1112131415}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
