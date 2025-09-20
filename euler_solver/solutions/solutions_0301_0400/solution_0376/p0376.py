#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 376: Nontransitive Sets of Dice.

Problem Statement:
    Consider the following set of dice with nonstandard pips:
    Die A: 1 4 4 4 4 4
    Die B: 2 2 2 5 5 5
    Die C: 3 3 3 3 3 6

    A game is played by two players picking a die in turn and rolling it.
    The player who rolls the highest value wins.

    If the first player picks die A and the second picks die B then
    P(second player wins) = 7/12 > 1/2.

    If the first player picks die B and the second picks die C then
    P(second player wins) = 7/12 > 1/2.

    If the first player picks die C and the second picks die A then
    P(second player wins) = 25/36 > 1/2.

    So whatever die the first player picks, the second player can pick
    another die and have a larger than 50% chance of winning.
    A set of dice having this property is called a nontransitive set of
    dice.

    We wish to investigate how many sets of nontransitive dice exist.
    We will assume the following conditions:
    - There are three six-sided dice with each side having between 1 and N
      pips, inclusive.
    - Dice with the same set of pips are equal, regardless of which side
      on the die the pips are located.
    - The same pip value may appear on multiple dice; if both players roll
      the same value neither player wins.
    - The sets of dice {A,B,C}, {B,C,A} and {C,A,B} are the same set.

    For N = 7 we find there are 9780 such sets.
    How many are there for N = 30?

URL: https://projecteuler.net/problem=376
"""
from typing import Any

euler_problem: int = 376
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 7}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
