#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 948: Left vs Right.

Problem Statement:
    Left and Right play a game with a word consisting of L's and R's, alternating turns.
    On Left's turn, Left can remove any positive number of letters, but not all the
    letters, from the left side of the word. Right does the same on Right's turn except
    that Right removes letters from the right side. The game continues until only one
    letter remains: if it is an 'L' then Left wins; if it is an 'R' then Right wins.

    Let F(n) be the number of words of length n where the player moving first, whether
    it's Left or Right, will win the game if both play optimally.

    You are given F(3)=4 and F(8)=181.

    Find F(60).

URL: https://projecteuler.net/problem=948
"""
from typing import Any

euler_problem: int = 948
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 60}, 'answer': None},
]
encrypted: str = (
    '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'
    'RT03v6biQ95bXpUMEirAPkslGwO0cltk'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
