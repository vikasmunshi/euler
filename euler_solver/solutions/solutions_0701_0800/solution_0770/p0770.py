#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 770: Delphi Flip.

Problem Statement:
    A and B play a game. A has originally 1 gram of gold and B has an unlimited
    amount. Each round goes as follows:

        A chooses and displays, x, a nonnegative real number no larger than the
        amount of gold that A has.
        Either B chooses to TAKE. Then A gives B x grams of gold.
        Or B chooses to GIVE. Then B gives A x grams of gold.

    B TAKEs n times and GIVEs n times after which the game finishes.

    Define g(X) to be the smallest value of n so that A can guarantee to have
    at least X grams of gold at the end of the game. You are given g(1.7) = 10.

    Find g(1.9999).

URL: https://projecteuler.net/problem=770
"""
from typing import Any

euler_problem: int = 770
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'X': 1.9999}, 'answer': None},
    {'category': 'dev', 'input': {'X': 1.7}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
