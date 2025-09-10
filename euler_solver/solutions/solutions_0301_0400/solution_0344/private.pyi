#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 344: Silver Dollar Game.

Problem Statement:
    One variant of N.G. de Bruijn's silver dollar game can be described as
    follows:

    On a strip of squares a number of coins are placed, at most one coin per
    square. Only one coin, called the silver dollar, has any value. Two
    players take turns making moves. At each turn a player must make either a
    regular or a special move.

    A regular move consists of selecting one coin and moving it one or more
    squares to the left. The coin cannot move out of the strip or jump on or
    over another coin.

    Alternatively, the player can choose to make the special move of pocketing
    the leftmost coin rather than making a regular move. If no regular moves
    are possible, the player is forced to pocket the leftmost coin.

    The winner is the player who pockets the silver dollar.

    A winning configuration is an arrangement of coins on the strip where the
    first player can force a win no matter what the second player does.

    Let W(n, c) be the number of winning configurations for a strip of n
    squares, c worthless coins and one silver dollar.

    You are given that W(10, 2) = 324 and W(100, 10) = 1514704946113500.

    Find W(1,000,000, 100) modulo the semiprime 1000,036,000,099
    (= 1,000,003 * 1,000,033).

Solution Approach:
    Model the game as an impartial combinatorial game and analyze positions by
    their canonical decomposition into independent gaps. Use Grundy/SG theory
    to characterize winning configurations or derive recursive counting rules.
    Count arrangements with dynamic programming over strip length and coin count,
    using combinatorial coefficients to account for placements of worthless coins.
    Compute counts modulo each prime factor and combine with CRT for the
    semiprime modulus. Aim for an algorithm roughly O(n * c) or O(n * c log n)
    in time and O(c) to O(n * c) in space with careful convolution/DP.

Answer: ...
URL: https://projecteuler.net/problem=344
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 344
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'c': 2}},
    {'category': 'main', 'input': {'n': 1000000, 'c': 100}},
    {'category': 'extra', 'input': {'n': 100000, 'c': 200}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_silver_dollar_game_p0344_s0(*, n: int, c: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))