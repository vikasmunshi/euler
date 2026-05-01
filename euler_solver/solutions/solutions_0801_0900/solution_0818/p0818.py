#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 818: SET.

Problem Statement:
    The SET card game is played with a pack of 81 distinct cards. Each card has four
    features (Shape, Color, Number, Shading). Each feature has three different variants
    (e.g. Color can be red, purple, green).

    A SET consists of three different cards such that each feature is either the same
    on each card or different on each card.

    For a collection C_n of n cards, let S(C_n) denote the number of SETs in C_n. Then
    define F(n) = sum over all collections C_n of S(C_n)^4, where C_n ranges through all
    collections of n cards (among the 81 cards).

    You are given F(3) = 1080 and F(6) = 159690960.

    Find F(12).

URL: https://projecteuler.net/problem=818
"""
from typing import Any

euler_problem: int = 818
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 12}, 'answer': None},
    {'category': 'extra', 'input': {'n': 15}, 'answer': None},
]
encrypted: str = (
    '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'
    'DqPHn8l6HRE='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
