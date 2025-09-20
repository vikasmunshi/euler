#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 687: Shuffling Cards.

Problem Statement:
    A standard deck of 52 playing cards, which consists of thirteen ranks (Ace, Two,
    ..., Ten, King, Queen and Jack) each in four suits (Clubs, Diamonds, Hearts and
    Spades), is randomly shuffled.  Let us call a rank perfect if no two cards of that
    same rank appear next to each other after the shuffle.

    It can be seen that the expected number of ranks that are perfect after a random
    shuffle equals 4324/425 ≈ 10.1741176471.

    Find the probability that the number of perfect ranks is prime. Give your answer
    rounded to 10 decimal places.

URL: https://projecteuler.net/problem=687
"""
from typing import Any

euler_problem: int = 687
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
