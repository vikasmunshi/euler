#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 905: Now I Know.

Problem Statement:
    Three epistemologists, known as A, B, and C, are in a room, each wearing a hat
    with a number on it. They have been informed beforehand that all three numbers
    are positive and that one of the numbers is the sum of the other two.

    Once in the room, they can see the numbers on each other's hats but not on their
    own. Starting with A and proceeding cyclically, each epistemologist must either
    honestly state "I don't know my number" or announce "Now I know my number!" which
    terminates the game.

    For instance, if their numbers are A=2, B=1, C=1 then A declares "Now I know" at
    the first turn. If their numbers are A=2, B=7, C=5 then "I don't know" is heard
    four times before B finally declares "Now I know" at the fifth turn.

    Let F(A,B,C) be the number of turns it takes until an epistemologist declares
    "Now I know", including the turn this declaration is made. So F(2,1,1)=1 and
    F(2,7,5)=5.

    Find the sum from a=1 to 7 and b=1 to 19 of F(a^b, b^a, a^b + b^a).

URL: https://projecteuler.net/problem=905
"""
from typing import Any

euler_problem: int = 905
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
