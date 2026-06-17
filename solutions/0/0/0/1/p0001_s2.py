#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 1: Multiples of 3 or 5 [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
    each part as sum(range(...)). O(limit)."""
    max_limit: int = runner.parse_int(args[0])
    return str(sum(range(0, max_limit, 3)) + sum(range(0, max_limit, 5)) - sum(range(0, max_limit, 15)))


if __name__ == "__main__":
    raise SystemExit(solve())
