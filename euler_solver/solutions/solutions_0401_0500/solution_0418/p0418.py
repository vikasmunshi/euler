#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 418: Factorisation Triples.

Problem Statement:
    Let n be a positive integer. An integer triple (a, b, c) is called a factorisation
    triple of n if:

        1 ≤ a ≤ b ≤ c
        a * b * c = n

    Define f(n) to be a + b + c for the factorisation triple (a, b, c) of n which
    minimises c / a. One can show that this triple is unique.

    For example, f(165) = 19, f(100100) = 142 and f(20!) = 4034872.

    Find f(43!).

URL: https://projecteuler.net/problem=418
"""
from typing import Any

euler_problem: int = 418
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
