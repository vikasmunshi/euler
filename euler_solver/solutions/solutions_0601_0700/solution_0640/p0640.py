#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 640: Shut the Box.

Problem Statement:
    Bob plays a single-player game of chance using two standard 6-sided dice and
    twelve cards numbered 1 to 12. When the game starts, all cards are placed
    face up on a table.

    Each turn, Bob rolls both dice, getting numbers x and y respectively, each in
    the range 1,...,6. He must choose amongst three options: turn over card x,
    card y, or card x+y. (If the chosen card is already face down, it is turned
    to face up, and vice versa.)

    If Bob manages to have all twelve cards face down at the same time, he wins.

    Alice plays a similar game, except that instead of dice she uses two fair
    coins, counting heads as 2 and tails as 1, and that she uses four cards
    instead of twelve. Alice finds that, with the optimal strategy for her game,
    the expected number of turns taken until she wins is approximately 5.673651.

    Assuming that Bob plays with an optimal strategy, what is the expected number
    of turns taken until he wins? Give your answer rounded to 6 places after the
    decimal point.

URL: https://projecteuler.net/problem=640
"""
from typing import Any

euler_problem: int = 640
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'UAShw4NaObm811QBjPleLDoktgTiCeoN'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
