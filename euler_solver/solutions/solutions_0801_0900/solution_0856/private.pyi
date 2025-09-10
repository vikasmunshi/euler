#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 856: Waiting for a Pair.

Problem Statement:
    A standard 52-card deck comprises 13 ranks in four suits. A pair is a set of two cards
    of the same rank.

    Cards are drawn, without replacement, from a well shuffled 52-card deck waiting for
    consecutive cards that form a pair. For example, the probability of finding a pair in
    the first two draws is 1/17.

    Cards are drawn until either such a pair is found or the pack is exhausted waiting for
    one. In the latter case we say that all 52 cards were drawn.

    Find the expected number of cards that were drawn. Give your answer rounded to eight
    places after the decimal point.

Solution Approach:
    Model the problem probabilistically using combinatorics and Markov chains or states
    tracking last card rank occurrences. Compute expected value by summing probabilities
    of first occurrence of a pair at each draw. Efficiently handle states and transitions
    to avoid excessive complexity.

Answer: ...
URL: https://projecteuler.net/problem=856
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 856
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_waiting_for_a_pair_p0856_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))