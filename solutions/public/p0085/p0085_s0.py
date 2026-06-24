#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 85: Counting Rectangles [Level 2]. """
from __future__ import annotations

import functools
import itertools
import typing

from solver.runners import runner


def num_rectangles(height: int, width: int) -> int:
    """Count sub-rectangles in a height x width grid by summing placements over every sub-rectangle size."""
    return sum(((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1)))


def delta_func(kv: tuple[int, typing.Any], *, target_num: int) -> int:
    """Absolute distance of a (count, value) entry's count from the target rectangle count."""
    return abs(kv[0] - target_num)


@runner.main
def solve(*args: str) -> str:
    """Brute-force position counting: scan every grid shape, recompute its exact rectangle count,
    and keep the area whose count is closest to the target; O(max_side^2) shapes with O(H*W) work each."""
    max_error = runner.parse_int(args[0])
    max_side = runner.parse_int(args[1])
    target_num_rectangles = runner.parse_int(args[2])

    delta = functools.partial(delta_func, target_num=target_num_rectangles)
    results: dict[int, tuple[int, int, int]] = {}
    for height, width in itertools.product(range(2, max_side), repeat=2):
        results[(num := num_rectangles(height, width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if runner.show:
        result = min(results.items(), key=delta)
        print(f"Grid with {result[0]} rectangles: {result[1]}")
    return str(min(results.items(), key=delta)[1][2])


if __name__ == "__main__":
    raise SystemExit(solve())
