#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 860: Gold and Silver Coin Game.

Problem Statement:
    Gary and Sally play a game using gold and silver coins arranged into a number
    of vertical stacks, alternating turns. On Gary's turn he chooses a gold coin
    and removes it from the game along with any other coins sitting on top. Sally
    does the same on her turn by removing a silver coin. The first player unable
    to make a move loses the game if both play optimally.

    An arrangement is called fair if the person moving first, whether it be Gary
    or Sally, will lose the game if both play optimally.

    Define F(n) to be the number of fair arrangements of n stacks, all of size 2.
    Different orderings of the stacks are to be counted separately, so F(2) = 4
    due to the following four arrangements:

    You are also given F(10) = 63594.

    Find F(9898). Give your answer modulo 989898989.

URL: https://projecteuler.net/problem=860
"""
from typing import Any

euler_problem: int = 860
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 9898}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
