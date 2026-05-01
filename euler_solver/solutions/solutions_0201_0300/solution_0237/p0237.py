#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 237: Tours on a 4 x N Playing Board.

Problem Statement:
    Let T(n) be the number of tours over a 4 x n playing board such that:
    The tour starts in the top left corner.
    The tour consists of moves that are up, down, left, or right one square.
    The tour visits each square exactly once.
    The tour ends in the bottom left corner.

    The diagram shows one tour over a 4 x 10 board.

    T(10) is 2329. What is T(10^12) modulo 10^8?

URL: https://projecteuler.net/problem=237
"""
from typing import Any

euler_problem: int = 237
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'jlfB4qDYAvKPqB8JBoxkaw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
