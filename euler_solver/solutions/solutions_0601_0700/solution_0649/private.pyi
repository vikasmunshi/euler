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

Solution Approach:
    Model the game as a combinatorial impartial game and use Sprague-Grundy theory.
    Calculate Grundy numbers for positions considering allowed moves (left or up by
    2, 3, 5, or 7). Use nim-sum of coin positions to determine winning states.
    Employ fast combinatorial counting and modular arithmetic for the large board
    and coin counts. Efficient DP or mathematical formula for M(n, c) is crucial.

Answer: ...
URL: https://projecteuler.net/problem=649
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 649
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'c': 1}},
    {'category': 'dev', 'input': {'n': 3, 'c': 2}},
    {'category': 'dev', 'input': {'n': 9, 'c': 3}},
    {'category': 'main', 'input': {'n': 10000019, 'c': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_low_prime_chessboard_nim_p0649_s0(*, n: int, c: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))