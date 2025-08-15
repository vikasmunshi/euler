#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 14: Longest Collatz Sequence.

Problem Statement:
    The following iterative sequence is defined for the set of positive integers:

        n → n/2  (n is even)
        n → 3n + 1  (n is odd)

    Using the rule above and starting with 13, we generate the following sequence:
    13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1.

    It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms.
    Although it has not been proved yet (Collatz Problem), it is thought that all starting
    numbers finish at 1.

    Which starting number, under one million, produces the longest chain?

    NOTE: Once the chain starts the terms are allowed to go above one million.

Solution Approach:
    Use iterative computation with memoization to compute chain lengths efficiently.
    For each number under one million, compute the Collatz sequence length and store in a
    cache to avoid recomputation. Track the number with the longest sequence.
    Time complexity roughly O(N) with memoization; space O(N).

Answer: 837799
URL: https://projecteuler.net/problem=14
"""
from __future__ import annotations

from typing import Any

from euler.logger import logger
from euler.maths.collartz_sequence import collatz_sequence_length
from euler.setup import evaluate, register_solution

euler_problem: int = 14
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_number': 1000000}},
    {'category': 'extended', 'input': {'max_number': 10000000}}
]


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:])
def solve_longest_collatz_sequence_p0014_s0(*, max_number: int) -> int:
    max_length, starting_number = 0, 0
    check_upto = int(max_number * 0.8)  # guesstimate

    for x in range(max_number, check_upto, -1):  # Start from max_number and decrease
        length = collatz_sequence_length(x)
        if length > max_length:
            max_length, starting_number = length, x

    return starting_number


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
