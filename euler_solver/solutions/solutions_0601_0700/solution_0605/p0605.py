#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 605: Pairwise Coin-Tossing Game.

Problem Statement:
    Consider an n-player game played in consecutive pairs: Round 1 takes place
    between players 1 and 2, round 2 takes place between players 2 and 3, and so
    on and so forth, all the way up to round n, which takes place between players
    n and 1. Then round n+1 takes place between players 1 and 2 as the entire
    cycle starts again.

    In other words, during round r, player ((r-1) mod n) + 1 faces off against
    player (r mod n) + 1.

    During each round, a fair coin is tossed to decide which of the two players
    wins that round. If any given player wins both rounds r and r+1, then that
    player wins the entire game.

    Let P_n(k) be the probability that player k wins in an n-player game, in the
    form of a reduced fraction. For example, P_3(1) = 12/49 and P_6(2) = 368/1323.

    Let M_n(k) be the product of the reduced numerator and denominator of P_n(k).
    For example, M_3(1) = 588 and M_6(2) = 486864.

    Find the last 8 digits of M_{10^8+7}(10^4+7).

URL: https://projecteuler.net/problem=605
"""
from typing import Any

euler_problem: int = 605
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6, 'k': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000007, 'k': 10007}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
