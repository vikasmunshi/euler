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

Solution Approach:
    The i-th draw is blue with probability p_i = 1/(i+1); draws are independent
    Bernoulli trials with varying p_i. Count blues B over n turns and require
    B > n/2 for a win.
    Use dynamic programming (convolution) to compute the distribution of B:
    iterate turns updating probabilities for each possible blue count.
    Use exact rational arithmetic (fractions.Fraction) to avoid precision error,
    then compute P_win and return floor(1 / P_win) as the maximum integer fund.
    Time complexity O(n^2), space O(n).

Answer: ...
URL: https://projecteuler.net/problem=121
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 121
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'turns': 4}},
    {'category': 'main', 'input': {'turns': 15}},
    {'category': 'extra', 'input': {'turns': 25}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_disc_game_prize_fund_p0121_s0(*, turns: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))