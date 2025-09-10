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

Solution Approach:
    Model the assignment as an online greedy partition of the natural numbers
    into disjoint chains (floors) where successive occupants on a chain sum
    to a perfect square. Key ideas: number theory (perfect squares), graph
    representation (edges when sums are square), and greedy chain decomposition.
    Factor the target product N to enumerate all factor pairs (f, r). For each
    pair we need the r-th element of the f-th chain; compute these by globally
    simulating assignments up to the maximum required chain length, or by an
    optimized construction that advances chains using a priority queue and a
    precomputed list of square numbers for quick lookups. Precompute squares
    up to the estimated bound to test square sums in O(1).
    Expected complexity: O(M log F) time and O(F) space where M is the number
    of people simulated (max person index needed) and F is number of floors.

Answer: ...
URL: https://projecteuler.net/problem=359
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 359
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'product': 6}},
    {'category': 'main', 'input': {'product': 71328803586048}},
    {'category': 'extra', 'input': {'product': 1000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hilberts_new_hotel_p0359_s0(*, product: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))