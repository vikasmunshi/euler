#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 459: Flipping Game.

Problem Statement:
    The flipping game is a two player game played on an N by N square board.
    Each square contains a disk with one side white and one side black.
    The game starts with all disks showing their white side.

    A turn consists of flipping all disks in a rectangle with the following properties:
        - the upper right corner of the rectangle contains a white disk
        - the rectangle width is a perfect square (1, 4, 9, 16, ...)
        - the rectangle height is a triangular number (1, 3, 6, 10, ...)
          where triangular numbers are defined as 1/2 n(n + 1) for positive integer n.

    Players alternate turns. A player wins by turning the grid all black.

    Let W(N) be the number of winning moves for the first player on an N by N board
    with all disks white, assuming perfect play.
    W(1) = 1, W(2) = 0, W(5) = 8 and W(10^2) = 31395.

    For N=5, the first player's eight winning first moves are shown in an accompanying image.

    Find W(10^6).

URL: https://projecteuler.net/problem=459
"""
from typing import Any

euler_problem: int = 459
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'board_size': 5}, 'answer': None},
    {'category': 'main', 'input': {'board_size': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
