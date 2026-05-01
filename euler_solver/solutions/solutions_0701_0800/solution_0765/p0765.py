#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 765: Trillionaire.

Problem Statement:
    Starting with 1 gram of gold you play a game. Each round you bet a certain amount
    of your gold: if you have x grams you can bet b grams for any 0 <= b <= x. You then
    toss an unfair coin: with a probability of 0.6 you double your bet (so you now have
    x+b), otherwise you lose your bet (so you now have x-b).

    Choosing your bets to maximize your probability of having at least a trillion (10^12)
    grams of gold after 1000 rounds, what is the probability that you become a trillionaire?

    All computations are assumed to be exact (no rounding), but give your answer rounded
    to 10 digits behind the decimal point.

URL: https://projecteuler.net/problem=765
"""
from typing import Any

euler_problem: int = 765
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
