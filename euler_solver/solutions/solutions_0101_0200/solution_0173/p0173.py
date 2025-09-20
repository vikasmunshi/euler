#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 173: Hollow Square Laminae I.

Problem Statement:
    We shall define a square lamina to be a square outline with a square "hole"
    so that the shape possesses vertical and horizontal symmetry. For example,
    using exactly thirty-two square tiles we can form two different square
    laminae.

    With one-hundred tiles, and not necessarily using all of the tiles at one
    time, it is possible to form forty-one different square laminae.

    Using up to one million tiles how many different square laminae can be
    formed?

URL: https://projecteuler.net/problem=173
"""
from typing import Any

euler_problem: int = 173
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 32}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
