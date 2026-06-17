#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 85: Counting Rectangles [Level 2]. """
from __future__ import annotations

import bisect
import functools
import typing

from solver.runners import runner


def num_rectangles_along_axis(length: int) -> int:
    """Triangular number T(length): the count of rectangles along one axis of given length."""
    return sum((length - num + 1 for num in range(1, length + 1)))


def delta_func(kv: tuple[int, typing.Any], *, target_num: int) -> int:
    """Absolute distance of a (count, value) entry's count from the target rectangle count."""
    return abs(kv[0] - target_num)


@runner.main
def solve(*args: str) -> str:
    """Triangular-number binary search: rectangle count factors as T(H)*T(W), so for each width
    binary-search the sorted triangular numbers for the nearest product to target, checking the two
    neighbours of the insertion point; O(max_side * log max_side)."""
    max_error = runner.parse_int(args[0])
    max_side = runner.parse_int(args[1])
    target_num_rectangles = runner.parse_int(args[2])

    delta = functools.partial(delta_func, target_num=target_num_rectangles)
    results: dict[int, tuple[int, int, int]] = {}
    numbers: tuple[int, ...] = tuple((num_rectangles_along_axis(length) for length in range(1, max_side)))
    len_numbers = len(numbers)
    num: int = 0
    for width, num_width in enumerate(numbers, start=1):
        j = bisect.bisect_left(a=numbers, x=target_num_rectangles // num_width)
        for height in (j + 1, j + 2):
            if 0 <= height - 1 < len_numbers:
                results[(num := (numbers[height - 1] * num_width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if runner.show:
        result = min(results.items(), key=delta)
        print(f"Grid with {result[0]} rectangles: {result[1]}")
    return str(min(results.items(), key=delta)[1][2])


if __name__ == "__main__":
    raise SystemExit(solve())
