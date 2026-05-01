#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 576: Irrational Jumps.

Problem Statement:
    A bouncing point moves counterclockwise along a circle with circumference 1 with
    jumps of constant length l < 1, until it hits a gap of length g < 1, that is placed
    in a distance d counterclockwise from the starting point. The gap does not include
    the starting point, that is g + d < 1.

    Let S(l, g, d) be the sum of the length of all jumps, until the point falls into
    the gap. It can be shown that S(l, g, d) is finite for any irrational jump size l,
    regardless of the values of g and d.
    Examples:
    S(sqrt(1/2), 0.06, 0.7) = 0.7071...,
    S(sqrt(1/2), 0.06, 0.3543) = 1.4142...,
    S(sqrt(1/2), 0.06, 0.2427) = 16.2634...

    Let M(n, g) be the maximum of the sum of S(sqrt(1/p), g, d) for all primes p ≤ n
    and any valid value of d.
    Examples:
    M(3, 0.06) = 29.5425..., since S(sqrt(1/2), 0.06, 0.2427) + S(sqrt(1/3), 0.06, 0.2427)
    = 29.5425... is the maximal reachable sum for g=0.06.
    M(10, 0.01) = 266.9010...

    Find M(100, 0.00002), rounded to 4 decimal places.

URL: https://projecteuler.net/problem=576
"""
from typing import Any

euler_problem: int = 576
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 100, 'g': 2e-05}, 'answer': None},
]
encrypted: str = (
    '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'
    'JRfqCA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
