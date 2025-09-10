#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 900: DistribuNim II.

Problem Statement:
    Two players play a game with at least two piles of stones. The players alternately
    take stones from one or more piles, subject to:

        1. the total number of stones taken is equal to the size of the smallest pile
           before the move;

        2. the move cannot take all the stones from a pile.

    The player that is unable to move loses.

    For example, if the piles are of sizes 2, 2 and 4 then there are four possible moves.
    (2,2,4) -> (1,1,4) by taking (1,1,0)
    (2,2,4) -> (1,2,3) by taking (1,0,1)
    (2,2,4) -> (2,1,3) by taking (0,1,1)
    (2,2,4) -> (2,2,2) by taking (0,0,2)

    Let t(n) be the smallest nonnegative integer k such that the position with n piles
    of n stones and a single pile of n+k stones is losing for the first player assuming
    optimal play. For example, t(1) = t(2) = 0 and t(3) = 2.

    Define S(N) = sum of t(n) for n = 1 to 2^N. You are given S(10) = 361522.

    Find S(10^4). Give your answer modulo 900497239.

Solution Approach:
    Analyze the combinatorial game using combinatorics and game theory to identify
    losing positions. Use number theory and dynamic programming to compute t(n)
    efficiently for large n. Employ modular arithmetic to handle large sums. The
    complexity depends on the pattern found in t(n) and efficient summation up to
    2^(10^4). Advanced mathematical insight or formulae may be necessary.

Answer: ...
URL: https://projecteuler.net/problem=900
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 900
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 2}},  # sum to 2^2=4 for a small test
    {'category': 'main', 'input': {'N': 10}},
    {'category': 'extra', 'input': {'N': 14}}  # larger but still feasible exponent
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_distribunim_ii_p0900_s0(*, N: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))