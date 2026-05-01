#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 560: Coprime Nim.

Problem Statement:
    Coprime Nim is just like ordinary normal play Nim, but the players may only
    remove a number of stones from a pile that is coprime with the current size
    of the pile. Two players remove stones in turn. The player who removes the
    last stone wins.

    Let L(n, k) be the number of losing starting positions for the first player,
    assuming perfect play, when the game is played with k piles, each having
    between 1 and n - 1 stones inclusively.

    For example, L(5, 2) = 6 since the losing initial positions are (1, 1),
    (2, 2), (2, 4), (3, 3), (4, 2) and (4, 4).
    You are also given L(10, 5) = 9964, L(10, 10) = 472400303,
    L(10^3, 10^3) mod 1,000,000,007 = 954021836.

    Find L(10^7, 10^7) mod 1,000,000,007.

URL: https://projecteuler.net/problem=560
"""
from typing import Any

euler_problem: int = 560
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'k': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 'k': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'lP45gCxEaeZCfN01SZCNuA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
