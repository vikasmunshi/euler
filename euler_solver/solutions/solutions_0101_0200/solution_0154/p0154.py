#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 154: Exploring Pascal's Pyramid.

Problem Statement:
    A triangular pyramid is constructed using spherical balls so that each ball
    rests on exactly three balls of the next lower level.

    Then, we calculate the number of paths leading from the apex to each
    position:

    A path starts at the apex and progresses downwards to any of the three
    spheres directly below the current position.

    Consequently, the number of paths to reach a certain position is the sum
    of the numbers immediately above it (depending on the position, there are
    up to three numbers above it).

    The result is Pascal's pyramid and the numbers at each level n are the
    coefficients of the trinomial expansion (x + y + z)^n.

    How many coefficients in the expansion of (x + y + z)^200000 are multiples
    of 10^12?

URL: https://projecteuler.net/problem=154
"""
from typing import Any

euler_problem: int = 154
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 200000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 500000}, 'answer': None},
]
encrypted: str = (
    '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'
    'VyWneQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
