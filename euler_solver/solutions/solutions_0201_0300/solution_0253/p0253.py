#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 253: Tidying Up A.

Problem Statement:
    A small child has a "number caterpillar" consisting of forty jigsaw pieces,
    each with one number on it, which, when connected together in a line,
    reveal the numbers 1 to 40 in order.

    Every night, the child's father has to pick up the pieces of the caterpillar
    that have been scattered across the play room. He picks up the pieces at
    random and places them in the correct order. As the caterpillar is built up
    in this way, it forms distinct segments that gradually merge together.
    The number of segments starts at zero (no pieces placed), generally
    increases up to about eleven or twelve, then tends to drop again before
    finishing at a single segment (all pieces placed).

    For example:
    Piece Placed  12  4  29  6  34  5  35  …
    Segments So Far 1   2   3   4   5   4   4   …

    Let M be the maximum number of segments encountered during a random
    tidy-up of the caterpillar.
    For a caterpillar of ten pieces, the number of possibilities for each M is:
    M = 1 -> 512
    M = 2 -> 250912
    M = 3 -> 1815264
    M = 4 -> 1418112
    M = 5 -> 144000

    so the most likely value of M is 3 and the average value is
    385643/113400 = 3.400732 (rounded to six decimal places).

    The most likely value of M for a forty-piece caterpillar is 11; but what is
    the average value of M?
    Give your answer rounded to six decimal places.

URL: https://projecteuler.net/problem=253
"""
from typing import Any

euler_problem: int = 253
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 40}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    '2yjxwH3c99UbBIow'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
