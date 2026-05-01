#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 859: Cookie Game.

Problem Statement:
    Odd and Even are playing a game with N cookies.

    The game begins with the N cookies divided into one or more piles,
    not necessarily of the same size. They then make moves in turn,
    starting with Odd.
    Odd's turn: Odd may choose any pile with an odd number of cookies,
    eat one and divide the remaining (if any) into two equal piles.
    Even's turn: Even may choose any pile with an even number of cookies,
    eat two of them and divide the remaining (if any) into two equal piles.
    The player that does not have a valid move loses the game.

    Let C(N) be the number of ways that N cookies can be divided so that
    Even has a winning strategy.
    For example, C(5) = 2 because there are two winning configurations
    for Even: a single pile containing all five cookies; three piles
    containing one, two and two cookies.
    You are also given C(16) = 64.

    Find C(300).

URL: https://projecteuler.net/problem=859
"""
from typing import Any

euler_problem: int = 859
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 300}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
