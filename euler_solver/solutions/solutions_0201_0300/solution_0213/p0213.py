#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 213: Flea Circus.

Problem Statement:
    A 30 x 30 grid of squares contains 900 fleas, initially one flea per
    square.
    When a bell is rung, each flea jumps to an adjacent square at random
    (usually 4 possibilities, except for fleas on the edge of the grid or at
    the corners).

    What is the expected number of unoccupied squares after 50 rings of the
    bell? Give your answer rounded to six decimal places.

URL: https://projecteuler.net/problem=213
"""
from typing import Any

euler_problem: int = 213
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'rings': 1}, 'answer': None},
    {'category': 'main', 'input': {'rings': 50}, 'answer': None},
    {'category': 'extra', 'input': {'rings': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    '4irIYA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
