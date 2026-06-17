#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 1: Multiples of 3 or 5 [Level 0]. """
from __future__ import annotations

from typing import Generator

from solver.runners import runner


def generate_arithmetic_series_loop(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    """Yield 0, d, 2d, ... below max_limit, advancing a running term."""
    term: int = 0
    while term < max_limit:
        yield term
        term += common_difference


@runner.main
def solve(*args: str) -> str:
    """Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
    each series from a state-variable generator and summed. O(limit)."""
    max_limit: int = runner.parse_int(args[0])
    return str(
        sum(generate_arithmetic_series_loop(3, max_limit=max_limit))
        + sum(generate_arithmetic_series_loop(5, max_limit=max_limit))
        - sum(generate_arithmetic_series_loop(15, max_limit=max_limit))
    )


if __name__ == "__main__":
    raise SystemExit(solve())
