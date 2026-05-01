#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 661: A Long Chess Match.

Problem Statement:
    Two friends A and B are great fans of Chess. They both enjoy playing the game,
    but after each game the player who lost the game would like to continue (to get
    back at the other player) and the player who won would prefer to stop (to finish on
    a high).

    So they come up with a plan. After every game, they would toss a (biased) coin with
    probability p of Heads (and hence probability 1-p of Tails). If they get Tails,
    they will continue with the next game. Otherwise they end the match. Also, after
    every game the players make a note of who is leading in the match.

    Let p_A denote the probability of A winning a game and p_B the probability of B winning
    a game. Accordingly 1-p_A-p_B is the probability that a game ends in a draw. Let E_A(p_A,
    p_B, p) denote the expected number of times A was leading in the match.

    For example, E_A(0.25,0.25,0.5) approximately 0.585786 and E_A(0.47,0.48,0.001) approximately
    377.471736, both rounded to six decimal places.

    Let H(n) = sum from k=3 to n of E_A(1/sqrt(k+3), 1/sqrt(k+3) + 1/k^2, 1/k^3).
    For example H(3) approximately 6.8345, rounded to 4 digits after the decimal point.

    Find H(50), rounded to 4 digits after the decimal point.

URL: https://projecteuler.net/problem=661
"""
from typing import Any

euler_problem: int = 661
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
