#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=85
"""
from __future__ import annotations

from bisect import bisect_left
from functools import partial
from itertools import product
from typing import Any, Dict, Tuple

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 85
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_error': 0, 'max_side': 10, 'target_num_rectangles': 18}, 'answer': 6},
    {'category': 'main', 'input': {'max_error': 2, 'max_side': 100, 'target_num_rectangles': 2000000}, 'answer': 2772},
]


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_rectangles_p0085_s0(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    for height, width in product(range(2, max_side), repeat=2):
        results[(num := num_rectangles(height, width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f'Grid with {result[0]} rectangles: {result[1]}')
    return min(results.items(), key=delta)[1][2]


def num_rectangles(height: int, width: int) -> int:
    return sum(((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1)))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_rectangles_p0085_s1(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    numbers: Tuple[int, ...] = tuple((num_rectangles_along_axis(length) for length in range(1, max_side)))
    len_numbers = len(numbers)
    num: int = 0
    for width, num_width in enumerate(numbers, start=1):
        j = bisect_left(a=numbers, x=target_num_rectangles // num_width)
        for height in (j + 1, j + 2):
            if 0 <= height - 1 < len_numbers:
                results[(num := (numbers[height - 1] * num_width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f'Grid with {result[0]} rectangles: {result[1]}')
    return min(results.items(), key=delta)[1][2]


def num_rectangles_along_axis(length: int) -> int:
    return sum((length - num + 1 for num in range(1, length + 1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
