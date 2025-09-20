#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 481: Chef Showdown.

Problem Statement:
    A group of chefs (numbered 1, 2, etc) participate in a turn-based strategic
    cooking competition. On each chef's turn, he/she cooks a dish and gives it
    to judges for taste-testing. Let S(k) be chef k's skill level (the
    probability the dish is rated favorably). If favorable, the chef must
    eliminate one other chef. The last chef remaining wins.

    The game begins with chef 1, then continues sequentially among remaining
    chefs, cycling repeatedly. All chefs optimize their chance to win
    assuming others do likewise. If multiple elimination options are equally
    optimal, the chef chooses the one with the next closest turn.

    Define W_n(k) as the probability that chef k wins in a competition with n
    chefs. For example, if S(1)=0.25, S(2)=0.5, and S(3)=1, then W_3(1)=0.29375.

    Going forward, assign S(k) = F_k / F_{n+1}, where F_k is the k-th Fibonacci
    number defined by F_k = F_{k-1} + F_{k-2} with base F_1=F_2=1.

    For n=7 chefs, the winning probabilities W_7(k) for k=1..7 are given
    rounded to 8 decimals, and the expected number of dishes cooked E(7) =
    42.28176050.

    Find E(14), the expected number of dishes cooked when starting with 14
    chefs, rounded to 8 decimal places.

URL: https://projecteuler.net/problem=481
"""
from typing import Any

euler_problem: int = 481
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 14}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
