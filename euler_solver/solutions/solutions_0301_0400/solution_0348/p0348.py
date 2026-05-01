#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 348: Sum of a Square and a Cube.

Problem Statement:
    Many numbers can be expressed as the sum of a square and a cube. Some of
    them in more than one way.

    Consider the palindromic numbers that can be expressed as the sum of a
    square and a cube, both greater than 1, in exactly 4 different ways.
    For example, 5229225 is a palindromic number and it can be expressed in
    exactly 4 different ways:
    2285^2 + 20^3
    2223^2 + 66^3
    1810^2 + 125^3
    1197^2 + 156^3

    Find the sum of the five smallest such palindromic numbers.

URL: https://projecteuler.net/problem=348
"""
from typing import Any

euler_problem: int = 348
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
