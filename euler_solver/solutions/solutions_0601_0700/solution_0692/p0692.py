#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 692: Siegbert and Jo.

Problem Statement:
    Siegbert and Jo take turns playing a game with a heap of N pebbles:
    1. Siegbert is the first to take some pebbles. He can take as many pebbles
       as he wants. (Between 1 and N inclusive.)
    2. In each of the following turns the current player must take at least one
       pebble and at most twice the amount of pebbles taken by the previous player.
    3. The player who takes the last pebble wins.

    Although Siegbert can always win by taking all the pebbles on his first turn,
    to make the game more interesting he chooses to take the smallest number of
    pebbles that guarantees he will still win (assuming both Siegbert and Jo play
    optimally for the rest of the game).

    Let H(N) be that minimal amount for a heap of N pebbles.
    H(1)=1, H(4)=1, H(17)=1, H(8)=8 and H(18)=5.

    Let G(n) be the sum from k=1 to n of H(k).
    G(13) = 43.

    Find G(23416728348467685).

URL: https://projecteuler.net/problem=692
"""
from typing import Any

euler_problem: int = 692
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 13}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 23416728348467685}, 'answer': None},
]
encrypted: str = (
    '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'
    's7TeUjkC8kE='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
