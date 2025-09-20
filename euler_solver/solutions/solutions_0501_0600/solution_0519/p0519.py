#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 519: Tricoloured Coin Fountains.

Problem Statement:
    An arrangement of coins in one or more rows with the bottom row being a
    block without gaps and every coin in a higher row touching exactly two coins
    in the row below is called a fountain of coins. Let f(n) be the number of
    possible fountains with n coins. For 4 coins there are three possible
    arrangements:
    Therefore f(4) = 3 while f(10) = 78.

    Let T(n) be the number of all possible colourings with three colours for
    all f(n) different fountains with n coins, given the condition that no two
    touching coins have the same colour. Below you see the possible colourings
    for one of the three valid fountains for 4 coins:
    You are given that T(4) = 48 and T(10) = 17760.

    Find the last 9 digits of T(20000).

URL: https://projecteuler.net/problem=519
"""
from typing import Any

euler_problem: int = 519
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    '8qpC0s5r5KcWwQV1'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
