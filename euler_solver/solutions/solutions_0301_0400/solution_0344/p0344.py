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

URL: https://projecteuler.net/problem=344
"""
from typing import Any

euler_problem: int = 344
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'c': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000, 'c': 100}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000, 'c': 200}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
