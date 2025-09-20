#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 313: Sliding Game.

Problem Statement:
    In a sliding game a counter may slide horizontally or vertically into an
    empty space. The objective is to move the red counter from the top-left
    corner of a grid to the bottom-right corner; the empty space starts in the
    bottom-right corner. For example, the game can be completed in five moves
    on a 2 by 2 grid.

    Let S(m,n) represent the minimum number of moves to complete the game on
    an m by n grid. For example, it can be verified that S(5,4) = 25.

    There are exactly 5482 grids for which S(m,n) = p^2, where p < 100 is
    prime.

    How many grids does S(m,n) = p^2, where p < 10^6 is prime?

URL: https://projecteuler.net/problem=313
"""
from typing import Any

euler_problem: int = 313
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'prime_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'prime_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
