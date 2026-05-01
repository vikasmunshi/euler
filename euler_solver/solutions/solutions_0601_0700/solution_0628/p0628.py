#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 628: Open Chess Positions.

Problem Statement:
    A position in chess is an (orientated) arrangement of chess pieces placed on a
    chessboard of given size. In the following, we consider all positions in which
    n pawns are placed on a n x n board in such a way, that there is a single pawn
    in every row and every column.

    We call such a position an open position, if a rook, starting at the (empty)
    lower left corner and using only moves towards the right or upwards, can reach
    the upper right corner without moving onto any field occupied by a pawn.

    Let f(n) be the number of open positions for an n x n chessboard.
    For example, f(3) = 2, illustrated by the two open positions for a 3 x 3
    chessboard below.

    You are also given f(5) = 70.

    Find f(10^8) modulo 1008691207.

URL: https://projecteuler.net/problem=628
"""
from typing import Any

euler_problem: int = 628
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
