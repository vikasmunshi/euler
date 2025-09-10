#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 602: Product of Head Counts.

Problem Statement:
    Alice enlists the help of some friends to generate a random number, using a
    single unfair coin. She and her friends sit around a table and, starting with
    Alice, they take it in turns to toss the coin. Everyone keeps a count of how
    many heads they obtain individually. The process ends as soon as Alice obtains
    a Head. At this point, Alice multiplies all her friends' Head counts together
    to obtain her random number.

    As an illustration, suppose Alice is assisted by Bob, Charlie, and Dawn, who
    are seated round the table in that order, and that they obtain the sequence of
    Head/Tail outcomes THHH—TTTT—THHT—H beginning and ending with Alice. Then Bob
    and Charlie each obtain 2 heads, and Dawn obtains 1 head. Alice's random number
    is therefore 2×2×1 = 4.

    Define e(n, p) to be the expected value of Alice's random number, where n is
    the number of friends helping (excluding Alice herself), and p is the
    probability of the coin coming up Tails.

    It turns out that, for any fixed n, e(n, p) is always a polynomial in p. For
    example, e(3, p) = p^3 + 4p^2 + p.

    Define c(n, k) to be the coefficient of p^k in the polynomial e(n, p). So
    c(3, 1) = 1, c(3, 2) = 4, and c(3, 3) = 1.

    You are given that c(100, 40) ≡ 986699437 (mod 10^9+7).

    Find c(10000000, 4000000) mod 10^9+7.

Solution Approach:
    Use combinatorics and probability theory to derive a formula for c(n, k).
    Consider dynamic programming or polynomial coefficient extraction methods.
    Efficient modular arithmetic is needed due to large parameters.
    Time complexity should be optimized using fast math and memory-efficient DP.

Answer: ...
URL: https://projecteuler.net/problem=602
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 602
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 10000000, 'k': 4000000, 'mod': 1000000007}},
    {'category': 'dev', 'input': {'n': 3, 'k': 2, 'mod': 1000000007}},
    {'category': 'dev', 'input': {'n': 100, 'k': 40, 'mod': 1000000007}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_product_of_head_counts_p0602_s0(*, n: int, k: int, mod: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))