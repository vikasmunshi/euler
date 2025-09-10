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

Solution Approach:
    Use dynamic programming with game theory and optimal strategies (minimax principle).
    The problem involves large N and a specific recurrence for sequence terms.
    Efficient matrix exponentiation or memoization and mathematical insight into the
    game's structure or sequence properties are required.
    Time complexity must be optimized to handle N=10^8 feasibly.

Answer: ...
URL: https://projecteuler.net/problem=477
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 477
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}},
    {'category': 'main', 'input': {'n': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_number_sequence_game_p0477_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))