#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 85: Counting Rectangles.

  Problem Statement:
    By counting carefully it can be seen that a rectangular grid measuring 3 by 2
    contains eighteen rectangles:

    Although there exists no rectangular grid that contains exactly two million
    rectangles, find the area of the grid with the nearest solution.

  Solution Approach:
    To solve this problem, consider how to count all possible rectangles in a
    grid of dimensions M by N. The total number of rectangles is given by the
    product of the number of ways to choose two vertical grid lines and two
    horizontal grid lines from the grid, which is (M x (M + 1) / 2) x (N x (N +
    1) / 2). To find the grid area with a number of rectangles nearest to two
    million, implement a search varying M and N and calculate the number of
    rectangles for each. Track the area M x N that yields the closest count.
    Efficiently prune the search space using bounding conditions since rectangle
    counts grow quickly with grid dimensions. This approach combines combinatorial
    counting with a numerical search for optimization.

  Test Cases:
    preliminary:
      max_error=0,
      max_side=10,
      target_num_rectangles=18,
      answer=6.

    main:
      max_error=2,
      max_side=100,
      target_num_rectangles=2000000,
      answer=2772.


  Answer: 2772
  URL: https://projecteuler.net/problem=85
"""
from __future__ import annotations

from bisect import bisect_left
from functools import partial
from itertools import product
from typing import Any, Dict, Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


@register_solution(euler_problem=85, test_case_category=TestCaseCategory.EXTENDED)
def counting_rectangles_product_height_width(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
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


@register_solution(euler_problem=85, test_case_category=TestCaseCategory.EXTENDED)
def counting_rectangles_pre_calculated_for_widths(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
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
    raise SystemExit(evaluate(euler_problem=85, time_out_in_seconds=300, mode='evaluate'))
