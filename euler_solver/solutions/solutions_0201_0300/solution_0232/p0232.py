#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 232: The Race.

Problem Statement:
    Two players share an unbiased coin and take it in turns to play The Race.

    On Player 1's turn, the coin is tossed once. If it comes up Heads, then
    Player 1 scores one point; if it comes up Tails, then no points are scored.

    On Player 2's turn, a positive integer, T, is chosen by Player 2 and the
    coin is tossed T times. If it comes up all Heads, then Player 2 scores
    2^{T-1} points; otherwise, no points are scored.

    Player 1 goes first and the winner is the first to 100 or more points.

    Player 2 will always select the number, T, of coin tosses that maximises
    the probability of winning.

    What is the probability that Player 2 wins?

    Give your answer rounded to eight decimal places in the form 0.abcdefgh.

URL: https://projecteuler.net/problem=232
"""
from typing import Any

euler_problem: int = 232
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200}, 'answer': None},
]
encrypted: str = (
    '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'
    '4a+DXhUxP4XPKTLL'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
