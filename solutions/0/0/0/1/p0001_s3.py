#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 1: Multiples of 3 or 5 [Level 0]. """
from __future__ import annotations

from typing import Generator

from solver.runners import runner


def generate_arithmetic_series_range(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    """Yield the arithmetic series 0, d, 2d, ... below max_limit."""
    for term in range(0, max_limit, common_difference):
        yield term


@runner.main
def solve(*args: str) -> str:
    """Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
    each series produced by a generator and summed. O(limit)."""
    max_limit: int = runner.parse_int(args[0])
    return str(
        sum(generate_arithmetic_series_range(3, max_limit=max_limit))
        + sum(generate_arithmetic_series_range(5, max_limit=max_limit))
        - sum(generate_arithmetic_series_range(15, max_limit=max_limit))
    )


if __name__ == "__main__":
    raise SystemExit(solve())
