#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 702: Jumping Flea.

Problem Statement:
    A regular hexagon table of side length N is divided into equilateral
    triangles of side length 1. An illustration for N = 3 is provided.

    A flea of negligible size starts at the centre of the table. At each
    step, it chooses one of the six corners of the table and jumps to
    the midpoint between its current position and the chosen corner.

    For every triangle T, define J(T) as the minimum number of jumps needed
    for the flea to reach the interior of T. Landing on an edge or vertex
    of T does not count.

    For example, J(T) = 3 for a given triangle marked in the picture: by
    jumping from the centre half way towards corner F, then towards C, then
    towards E.

    Let S(N) be the sum of J(T) for all the upper-pointing triangles T in
    the upper half of the table. For N=3, these triangles are shown in black.

    Given S(3) = 42, S(5) = 126, S(123) = 167178, and S(12345) = 3185041956.

    Find S(123456789).

URL: https://projecteuler.net/problem=702
"""
from typing import Any

euler_problem: int = 702
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 3}, 'answer': None},
    {'category': 'main', 'input': {'N': 123456789}, 'answer': None},
    {'category': 'extra', 'input': {'N': 12345}, 'answer': None},
]
encrypted: str = (
    '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'
    'n3TLjWKjNHYgWO4TIPyi/yhT8iqqxv8Q'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
