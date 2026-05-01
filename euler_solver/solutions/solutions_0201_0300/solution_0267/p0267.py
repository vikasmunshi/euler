#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 267: Billionaire.

Problem Statement:
    You are given a unique investment opportunity.
    Starting with £1 of capital, you can choose a fixed proportion, f, of your
    capital to bet on a fair coin toss repeatedly for 1000 tosses.
    Your return is double your bet for heads and you lose your bet for tails.
    For example, if f = 1/4, for the first toss you bet £0.25, and if heads
    comes up you win £0.5 and so then have £1.5. You then bet £0.375 and if
    the second toss is tails, you have £1.125.
    Choosing f to maximize your chances of having at least £1,000,000,000
    after 1,000 flips, what is the chance that you become a billionaire?
    All computations are assumed to be exact (no rounding), but give your
    answer rounded to 12 digits behind the decimal point in the form
    0.abcdefghijkl.

URL: https://projecteuler.net/problem=267
"""
from typing import Any

euler_problem: int = 267
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_flips': 10, 'target': 1000}, 'answer': None},
    {'category': 'main', 'input': {'num_flips': 1000, 'target': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'num_flips': 2000, 'target': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'YKGpmA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
