#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 1: Multiples of 3 or 5 [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Multiples of 3 or 5 below the limit by scanning every term and testing
    divisibility. O(limit)."""
    max_limit: int = runner.parse_int(args[0])
    result: int = 0
    for term in range(0, max_limit):
        if term % 3 == 0 or term % 5 == 0:
            result += term
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
