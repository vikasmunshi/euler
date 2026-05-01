#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 787: Bézout's Game.

Problem Statement:
    Two players play a game with two piles of stones. They take alternating turns.
    If there are currently a stones in the first pile and b stones in the second,
    a turn consists of removing c≥0 stones from the first pile and d≥0 from the
    second in such a way that a d − b c = ±1. The winner is the player who first
    empties one of the piles.

    Note that the game is only playable if the sizes of the two piles are coprime.

    A game state (a, b) is a winning position if the next player can guarantee a win
    with optimal play. Define H(N) to be the number of winning positions (a, b) with
    gcd(a,b)=1, a > 0, b > 0 and a + b ≤ N. Note the order matters, so for example
    (2,1) and (1,2) are distinct positions.

    You are given H(4)=5 and H(100)=2043.

    Find H(10^9).

URL: https://projecteuler.net/problem=787
"""
from typing import Any

euler_problem: int = 787
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
