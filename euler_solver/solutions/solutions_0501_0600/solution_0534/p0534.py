#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 534: Weak Queens.

Problem Statement:
    The classical eight queens puzzle is the well known problem of placing eight
    chess queens on an 8 x 8 chessboard so that no two queens threaten each other.
    Allowing configurations to reappear in rotated or mirrored form, a total of 92
    distinct configurations can be found for eight queens. The general case asks
    for the number of distinct ways of placing n queens on an n x n board, e.g.
    you can find 2 distinct configurations for n=4.

    Let's define a weak queen on an n x n board to be a piece which can move any
    number of squares if moved horizontally, but a maximum of n - 1 - w squares if
    moved vertically or diagonally, 0 <= w < n being the "weakness factor". For
    example, a weak queen on an n x n board with a weakness factor of w=1 located
    in the bottom row will not be able to threaten any square in the top row as
    the weak queen would need to move n - 1 squares vertically or diagonally to get
    there, but may only move n - 2 squares in these directions. In contrast, the
    weak queen is not handicapped horizontally, thus threatening every square in
    its own row, independently from its current position in that row.

    Let Q(n,w) be the number of ways n weak queens with weakness factor w can be
    placed on an n x n board so that no two queens threaten each other. It can be
    shown, for example, that Q(4,0)=2, Q(4,2)=16 and Q(4,3)=256.

    Let S(n) = sum over w=0 to n-1 of Q(n,w).

    You are given that S(4)=276 and S(5)=3347.

    Find S(14).

URL: https://projecteuler.net/problem=534
"""
from typing import Any

euler_problem: int = 534
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 14}, 'answer': None},
]
encrypted: str = (
    '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'
    'Ta688VvBqxRBQqJDFOWxaA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
