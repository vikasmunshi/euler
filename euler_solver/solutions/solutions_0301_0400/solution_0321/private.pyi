#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 321: Swapping Counters.

Problem Statement:
    A horizontal row comprising of 2n + 1 squares has n red counters placed at one
    end and n blue counters at the other end, separated by a single empty square
    in the centre. For example, when n = 3.

    A counter can move from one square to the next (slide) or can jump over
    another counter (hop) as long as the square next to that counter is unoccupied.

    Let M(n) represent the minimum number of moves/actions to completely reverse
    the positions of the coloured counters; that is, move all the red counters
    to the right and all the blue counters to the left.

    It can be verified M(3) = 15, which also happens to be a triangle number.

    If we create a sequence based on the values of n for which M(n) is a
    triangle number then the first five terms would be:
    1, 3, 10, 22, and 63, and their sum would be 99.

    Find the sum of the first forty terms of this sequence.

Solution Approach:
    Observe the known formula M(n) = n(n + 2) for the minimal moves (classic
    frogs/swapping puzzle). We seek n such that n(n+2) is a triangular number
    T_k = k(k+1)/2. This Diophantine condition can be rearranged to a Pell-
    type equation. Solve the Pell recurrence to generate all solutions (use the
    fundamental solution and a linear recurrence for successive terms).

    Key ideas: number theory, Pell equations, recurrence relations, big integer
    arithmetic. Generate the sequence of n values from the Pell solution and
    sum the first terms requested. Time: O(t) big-integer ops for t terms.
    Space: O(1) extra besides integers.

Answer: ...
URL: https://projecteuler.net/problem=321
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 321
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'terms': 5}},
    {'category': 'main', 'input': {'terms': 40}},
    {'category': 'extra', 'input': {'terms': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_swapping_counters_p0321_s0(*, terms: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))