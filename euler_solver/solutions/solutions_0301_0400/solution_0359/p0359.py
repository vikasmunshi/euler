#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 359: Hilbert's New Hotel.

Problem Statement:
    An infinite number of people (numbered 1, 2, 3, etc.) are lined up to get
    a room at Hilbert's newest infinite hotel. The hotel contains an infinite
    number of floors (numbered 1, 2, 3, etc.), and each floor contains an
    infinite number of rooms (numbered 1, 2, 3, etc.).

    Initially the hotel is empty. Hilbert declares a rule on how the n-th
    person is assigned a room: person n gets the first vacant room in the
    lowest numbered floor satisfying either of the following:
        - the floor is empty
        - the floor is not empty, and if the latest person taking a room in
          that floor is m, then m + n is a perfect square

    Person 1 gets room 1 in floor 1 since floor 1 is empty.
    Person 2 does not get room 2 in floor 1 since 1 + 2 = 3 is not a perfect
    square. Person 2 instead gets room 1 in floor 2 since floor 2 is empty.
    Person 3 gets room 2 in floor 1 since 1 + 3 = 4 is a perfect square.

    Eventually, every person in the line gets a room in the hotel.

    Define P(f, r) to be n if person n occupies room r in floor f, and 0 if
    no person occupies the room. Examples:
    P(1, 1) = 1
    P(1, 2) = 3
    P(2, 1) = 2
    P(10, 20) = 440
    P(25, 75) = 4863
    P(99, 100) = 19454

    Find the sum of all P(f, r) for all positive f and r such that
    f * r = 71328803586048 and give the last 8 digits as your answer.

URL: https://projecteuler.net/problem=359
"""
from typing import Any

euler_problem: int = 359
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'product': 6}, 'answer': None},
    {'category': 'main', 'input': {'product': 71328803586048}, 'answer': None},
    {'category': 'extra', 'input': {'product': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
