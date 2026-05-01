#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 808: Reversible Prime Squares.

Problem Statement:
    Both 169 and 961 are the square of a prime. 169 is the reverse of 961.

    We call a number a reversible prime square if:
        1) It is not a palindrome, and
        2) It is the square of a prime, and
        3) Its reverse is also the square of a prime.

    169 and 961 are not palindromes, so both are reversible prime squares.

    Find the sum of the first 50 reversible prime squares.

URL: https://projecteuler.net/problem=808
"""
from typing import Any

euler_problem: int = 808
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'count': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
