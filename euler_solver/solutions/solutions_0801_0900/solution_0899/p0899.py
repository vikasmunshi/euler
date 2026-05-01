#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 899: DistribuNim I.

Problem Statement:
    Two players play a game with two piles of stones. The players alternately take
    stones from one or both piles, subject to:

        1. the total number of stones taken is equal to the size of the smallest pile
           before the move;
        2. the move cannot take all the stones from a pile.

    The player that is unable to move loses.

    For example, if the piles are of sizes 3 and 5 then there are three possible moves.
    (3,5) ->(2,1) (1,4)      (3,5) ->(1,2) (2,3)      (3,5) ->(0,3) (3,2)

    Let L(n) be the number of ordered pairs (a,b) with 1 ≤ a,b ≤ n such that the initial
    game position with piles of sizes a and b is losing for the first player assuming
    optimal play.

    You are given L(7) = 21 and L(7^2) = 221.

    Find L(7^17).

URL: https://projecteuler.net/problem=899
"""
from typing import Any

euler_problem: int = 899
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'n': 232630513987207}, 'answer': None},
]
encrypted: str = (
    '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'
    '4FlXWQ1UIEqnbxWI'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
