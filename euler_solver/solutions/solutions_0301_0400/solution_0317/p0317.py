#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 317: Firecracker.

Problem Statement:
    A firecracker explodes at a height of 100 m above level ground. It breaks into
    a large number of very small fragments, which move in every direction; all of
    them have the same initial velocity of 20 m/s.

    We assume that the fragments move without air resistance, in a uniform
    gravitational field with g = 9.81 m/s^2.

    Find the volume (in m^3) of the region through which the fragments move
    before reaching the ground. Give your answer rounded to four decimal places.

URL: https://projecteuler.net/problem=317
"""
from typing import Any

euler_problem: int = 317
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'height': 10.0, 'speed': 5.0, 'g': 9.81}, 'answer': None},
    {'category': 'main', 'input': {'height': 100.0, 'speed': 20.0, 'g': 9.81}, 'answer': None},
    {'category': 'extra', 'input': {'height': 500.0, 'speed': 50.0, 'g': 9.81}, 'answer': None},
]
encrypted: str = (
    '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'
    'WdqXxw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
