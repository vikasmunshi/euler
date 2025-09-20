#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 523: First Sort I.

Problem Statement:
    Consider the following algorithm for sorting a list:

    1. Starting from the beginning of the list, check each pair of adjacent elements in turn.
    2. If the elements are out of order:
        a. Move the smallest element of the pair at the beginning of the list.
        b. Restart the process from step 1.
    3. If all pairs are in order, stop.

    For example, the list {4 1 3 2} is sorted as follows:
    - 4 1 3 2 (4 and 1 are out of order so move 1 to the front of the list)
    - 1 4 3 2 (4 and 3 are out of order so move 3 to the front of the list)
    - 3 1 4 2 (3 and 1 are out of order so move 1 to the front of the list)
    - 1 3 4 2 (4 and 2 are out of order so move 2 to the front of the list)
    - 2 1 3 4 (2 and 1 are out of order so move 1 to the front of the list)
    - 1 2 3 4 (The list is now sorted)

    Let F(L) be the number of times step 2a is executed to sort list L.
    For example, F({4 1 3 2}) = 5.

    Let E(n) be the expected value of F(P) over all permutations P of the integers {1, 2, ..., n}.
    You are given E(4) = 3.25 and E(10) = 115.725.

    Find E(30). Give your answer rounded to two digits after the decimal point.

URL: https://projecteuler.net/problem=523
"""
from typing import Any

euler_problem: int = 523
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 30}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
