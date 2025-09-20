#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 436: Unfair Wager.

Problem Statement:
    Julie proposes the following wager to her sister Louise.
    She suggests they play a game of chance to determine who will wash the dishes.
    For this game, they shall use a generator of independent random numbers uniformly
    distributed between 0 and 1.
    The game starts with S = 0.
    The first player, Louise, adds to S different random numbers from the generator until
    S > 1 and records her last random number 'x'.
    The second player, Julie, continues adding to S different random numbers from the
    generator until S > 2 and records her last random number 'y'.
    The player with the highest number wins and the loser washes the dishes, i.e. if y > x
    the second player wins.

    For example, if the first player draws 0.62 and 0.44, the first player turn ends since
    0.62+0.44 > 1 and x = 0.44.
    If the second player draws 0.1, 0.27 and 0.91, the second player turn ends since
    0.62+0.44+0.1+0.27+0.91 > 2 and y = 0.91.
    Since y > x, the second player wins.

    Louise thinks about it for a second, and objects: "That's not fair".
    What is the probability that the second player wins?
    Give your answer rounded to 10 places behind the decimal point in the form 0.abcdefghij.

URL: https://projecteuler.net/problem=436
"""
from typing import Any

euler_problem: int = 436
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '9rLwH6HzDeYFe0Hw0adonw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
