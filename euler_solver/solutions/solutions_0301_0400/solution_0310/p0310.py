#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 310: Nim Square.

Problem Statement:
    Alice and Bob play the game Nim Square.
    Nim Square is like ordinary three-heap normal-play Nim, but players may only
    remove a square number of stones from a heap.
    The number of stones in the three heaps is represented by the ordered triple
    (a, b, c). If 0 <= a <= b <= c <= 29 then the number of losing positions for
    the next player is 1160.
    Find the number of losing positions for the next player if 0 <= a <= b <= c
    <= 100000.

URL: https://projecteuler.net/problem=310
"""
from typing import Any

euler_problem: int = 310
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 29}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
    'wlNHmVwWXPU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
