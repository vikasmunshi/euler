#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 477: Number Sequence Game.

Problem Statement:
    The number sequence game starts with a sequence S of N numbers written on a line.

    Two players alternate turns. The players on their respective turns must select and
    remove either the first or the last number remaining in the sequence.

    A player's own score is the sum of all the numbers that player has taken. Each player
    attempts to maximize their own sum.

    If N = 4 and S = {1, 2, 10, 3}, then each player maximizes their own score as follows:
        Player 1: removes the first number (1)
        Player 2: removes the last number from the remaining sequence (3)
        Player 1: removes the last number from the remaining sequence (10)
        Player 2: removes the remaining number (2)

    Player 1 score is 1 + 10 = 11.

    Let F(N) be the score of player 1 if both players follow the optimal strategy for the
    sequence S = {s_1, s_2, ..., s_N} defined as:
        s_1 = 0
        s_{i+1} = (s_i^2 + 45) modulo 1 000 000 007

    The sequence begins with S = {0, 45, 2070, 4284945, 753524550, 478107844, 894218625, ...}.

    You are given F(2)=45, F(4)=4284990, F(100)=26365463243, F(10^4)=2495838522951.

    Find F(10^8).

URL: https://projecteuler.net/problem=477
"""
from typing import Any

euler_problem: int = 477
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '9wR1P8nO7P01PK1dHAStf8ZJHuw3jd2v'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
