#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 949: Left vs Right II.

Problem Statement:
    Left and Right play a game with a number of words, each consisting of L's and R's,
    alternating turns. On Left's turn, for each word, Left can remove any number of letters
    (possibly zero), but not all the letters, from the left side of the word. However,
    at least one letter must be removed from at least one word. Right does the same on
    Right's turn except that Right removes letters from the right side of each word.
    The game continues until each word is reduced to a single letter. If there are more
    L's than R's remaining then Left wins; otherwise if there are more R's than L's then
    Right wins. In this problem we only consider games with an odd number of words, thus
    making ties impossible.

    Let G(n, k) be the number of ways of choosing k words of length n, for which Right
    has a winning strategy when Left plays first. Different orderings of the same set of
    words are to be counted separately.

    It can be seen that G(2, 3) = 14 due to the following solutions (and their reorderings):
        (LL, RR, RR): 3 orderings
        (LR, LR, LR): 1 ordering
        (LR, LR, RR): 3 orderings
        (LR, RR, RR): 3 orderings
        (RL, RR, RR): 3 orderings
        (RR, RR, RR): 1 ordering

    You are also given G(4, 3) = 496 and G(8, 5) = 26359197010.

    Find G(20, 7) giving your answer modulo 1001001011.

URL: https://projecteuler.net/problem=949
"""
from typing import Any

euler_problem: int = 949
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 20, 'k': 7, 'mod': 1001001011}, 'answer': None},
]
encrypted: str = (
    '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'
    'WxH1h0GmCmi+iYLl66OGb9tVq9VzpmybLUgFDA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
