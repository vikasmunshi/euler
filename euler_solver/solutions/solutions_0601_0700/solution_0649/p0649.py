#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 649: Low-Prime Chessboard Nim.

Problem Statement:
    Alice and Bob are taking turns playing a game consisting of c different coins
    on a chessboard of size n by n.

    The game may start with any arrangement of c coins in squares on the board.
    It is possible at any time for more than one coin to occupy the same square
    on the board at the same time. The coins are distinguishable, so swapping two
    coins gives a different arrangement if (and only if) they are on different
    squares.

    On a given turn, the player must choose a coin and move it either left or up
    2, 3, 5, or 7 spaces in a single direction. The only restriction is that the
    coin cannot move off the edge of the board.

    The game ends when a player is unable to make a valid move, thereby granting
    the other player the victory.

    Assuming that Alice goes first and that both players are playing optimally,
    let M(n, c) be the number of possible starting arrangements for which Alice
    can ensure her victory, given a board of size n by n with c distinct coins.

    For example, M(3, 1) = 4, M(3, 2) = 40, and M(9, 3) = 450304.

    What are the last 9 digits of M(10 000 019, 100)?

URL: https://projecteuler.net/problem=649
"""
from typing import Any

euler_problem: int = 649
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'c': 1}, 'answer': None},
    {'category': 'dev', 'input': {'n': 3, 'c': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 9, 'c': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000019, 'c': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    '4jCQ6N4cIPBieIvMbfBBIVVIJkY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
