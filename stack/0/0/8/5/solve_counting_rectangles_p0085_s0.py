#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0085/p0085.py :: solve_counting_rectangles_p0085_s0.

Project Euler Problem 85: Counting Rectangles.

Problem Statement:
    By counting carefully it can be seen that a rectangular grid measuring 3 by 2
    contains eighteen rectangles:

    Although there exists no rectangular grid that contains exactly two million
    rectangles, find the area of the grid with the nearest solution.

Solution Approach:
    Use combinatorics to count rectangles in an n by m grid as (n(n+1)/2)*(m(m+1)/2).
    Search for n, m to minimize |n(n+1)m(m+1)/4 - 2,000,000|, limiting search by
    bounding n and m using approximate square root of target.
    Efficient nested loops or binary search can be used for O(n sqrt(target)) or better
    with pruning.

Answer: 2772
URL: https://projecteuler.net/problem=85"""
from __future__ import annotations

import sys
from functools import partial
from itertools import product
from typing import Any, Dict, Tuple


def num_rectangles(height: int, width: int) -> int:
    return sum(((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1)))


def show_solution() -> bool:
    return '--show' in sys.argv


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


def solve(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    for height, width in product(range(2, max_side), repeat=2):
        results[(num := num_rectangles(height, width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f'Grid with {result[0]} rectangles: {result[1]}', file=sys.stderr)
    return min(results.items(), key=delta)[1][2]


if __name__ == '__main__':
    print(solve(max_error=int(sys.argv[1]), max_side=int(sys.argv[2]), target_num_rectangles=int(sys.argv[3])))
