#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 527: Randomized Binary Search.

Problem Statement:
    A secret integer t is selected at random within the range 1 ≤ t ≤ n.

    The goal is to guess the value of t by making repeated guesses, via integer g.
    After a guess is made, there are three possible outcomes, in which it will be
    revealed that either g < t, g = t, or g > t. Then the process can repeat as
    necessary.

    Normally, the number of guesses required on average can be minimized with a
    binary search: Given a lower bound L and upper bound H (initialized to L = 1 and
    H = n), let g = floor((L+H)/2) where floor is the integer floor function. If g = t,
    the process ends. Otherwise, if g < t, set L = g+1, but if g > t instead, set H =
    g - 1. After setting the new bounds, the search process repeats, and ultimately ends
    once t is found. Even if t can be deduced without searching, assume that a search
    will be required anyway to confirm the value.

    Your friend Bob believes that the standard binary search is not that much better than
    his randomized variant: Instead of setting g = floor((L+H)/2), simply let g be a random
    integer between L and H, inclusive. The rest of the algorithm is the same as the
    standard binary search. This new search routine will be referred to as a random binary
    search.

    Given that 1 ≤ t ≤ n for random t, let B(n) be the expected number of guesses needed
    to find t using the standard binary search, and let R(n) be the expected number of
    guesses needed to find t using the random binary search. For example, B(6) =
    2.33333333 and R(6) = 2.71666667 when rounded to 8 decimal places.

    Find R(10^10) - B(10^10) rounded to 8 decimal places.

URL: https://projecteuler.net/problem=527
"""
from typing import Any

euler_problem: int = 527
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '2S/DocZ+40hzseLL'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
