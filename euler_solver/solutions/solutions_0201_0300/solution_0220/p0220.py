#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 220: Heighway Dragon.

Problem Statement:
    Let D_0 be the two-letter string "Fa". For n≥1, derive D_n from D_{n-1}
    by the string-rewriting rules:
    "a" -> "aRbFR"
    "b" -> "LFaLb"
    Thus, D_0 = "Fa", D_1 = "FaRbFR", D_2 = "FaRbFRRLFaLbFR", and so on.
    These strings are instructions: "F" means draw forward one unit, "L"
    turn left 90°, "R" turn right 90°, and "a" and "b" are ignored. The
    initial position is (0,0), pointing up toward (0,1).
    D_n is the Heighway Dragon of order n. For example, in D_10 the
    position after 500 steps is (18,16).
    What is the position of the cursor after 10^12 steps in D_50?
    Give your answer as x,y with no spaces.

URL: https://projecteuler.net/problem=220
"""
from typing import Any

euler_problem: int = 220
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'steps': 500, 'order': 10}, 'answer': None},
    {'category': 'main', 'input': {'steps': 1000000000000, 'order': 50}, 'answer': None},
    {'category': 'extra', 'input': {'steps': 1000000, 'order': 25}, 'answer': None},
]
encrypted: str = (
    '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'
    'Q+tf7qYKypnDyL5dLLiuY4JDQsg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
