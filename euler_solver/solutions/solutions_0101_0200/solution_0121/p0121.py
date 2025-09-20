#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 121: Disc Game Prize Fund.

Problem Statement:
    A bag contains one red disc and one blue disc. In a game of chance a player
    takes a disc at random and its colour is noted. After each turn the disc is
    returned to the bag, an extra red disc is added, and another disc is taken
    at random.
    The player pays £1 to play and wins if they have taken more blue discs than
    red discs at the end of the game.
    If the game is played for four turns, the probability of a player winning is
    exactly 11/120, and so the maximum prize fund the banker should allocate
    for winning in this game would be £10 before they would expect to incur a
    loss. Note that any payout will be a whole number of pounds and also
    includes the original £1 paid to play the game, so in the example the
    player actually wins £9.
    Find the maximum prize fund that should be allocated to a single game in
    which fifteen turns are played.

URL: https://projecteuler.net/problem=121
"""
from typing import Any

euler_problem: int = 121
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'turns': 4}, 'answer': None},
    {'category': 'main', 'input': {'turns': 15}, 'answer': None},
    {'category': 'extra', 'input': {'turns': 25}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
