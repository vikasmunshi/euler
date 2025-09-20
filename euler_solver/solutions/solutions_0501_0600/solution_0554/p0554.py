#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 554: Centaurs on a Chess Board.

Problem Statement:
    On a chess board, a centaur moves like a king or a knight. The diagram below shows
    the valid moves of a centaur (represented by an inverted king) on an 8 x 8 board.

    It can be shown that at most n^2 non-attacking centaurs can be placed on a board
    of size 2n x 2n.
    Let C(n) be the number of ways to place n^2 centaurs on a 2n x 2n board so that
    no centaur attacks another directly.
    For example C(1) = 4, C(2) = 25, C(10) = 1477721.

    Let F_i be the i-th Fibonacci number defined as F_1 = F_2 = 1 and F_i = F_{i - 1}
    + F_{i - 2} for i > 2.

    Find (sum from i=2 to 90 of C(F_i)) modulo (10^8 + 7).

URL: https://projecteuler.net/problem=554
"""
from typing import Any

euler_problem: int = 554
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 90}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
