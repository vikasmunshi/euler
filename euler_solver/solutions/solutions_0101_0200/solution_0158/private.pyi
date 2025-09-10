#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 158: Lexicographical Neighbours.

Problem Statement:
    Taking three different letters from the 26 letters of the alphabet,
    character strings of length three can be formed. Examples are 'abc',
    'hat' and 'zyx'. When we study these three examples we see that for
    'abc' two characters come lexicographically after its neighbour to the
    left. For 'hat' there is exactly one character that comes lexicographically
    after its neighbour to the left. For 'zyx' there are zero characters that
    come lexicographically after its neighbour to the left. In all there are
    10400 strings of length 3 for which exactly one character comes
    lexicographically after its neighbour to the left.

    We now consider strings of n <= 26 different characters from the alphabet.
    For every n, p(n) is the number of strings of length n for which exactly
    one character comes lexicographically after its neighbour to the left.

    What is the maximum value of p(n)?

Solution Approach:
    Use combinatorics and Eulerian numbers. For permutations of n distinct
    letters the number with exactly one ascent equals the Eulerian number A(n,1).
    For this case p(n) = C(26, n) * A(n, 1) and A(n, 1) = 2^n - n - 1.
    Evaluate p(n) for n = 1..26 and return the maximum. Time O(26) and constant
    space; computations use integer arithmetic only.

Answer: ...
URL: https://projecteuler.net/problem=158
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 158
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 3}},
    {'category': 'main', 'input': {'max_limit': 26}},
    {'category': 'extra', 'input': {'max_limit': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_lexicographical_neighbours_p0158_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))