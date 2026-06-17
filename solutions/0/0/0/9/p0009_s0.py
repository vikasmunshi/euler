#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 9: Special Pythagorean Triplet [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Bounded two-variable search: the linear constraint fixes c = S - a - b, so only
    a (1..S/4) and b (a..S/2) are searched; return a*b*c on the first Pythagorean hit. O(S^2)."""
    sum_sides = runner.parse_int(args[0])

    try:
        return str(next(
            (
                a * b * c
                for a in range(1, sum_sides // 4 + 1)
                for b in range(a, sum_sides // 2)
                for c in (sum_sides - a - b,)
                if a**2 + b**2 == c**2
            )
        ))
    except StopIteration:
        raise ValueError(f"No Pythagorean triplet exists with sum {sum_sides}")


if __name__ == "__main__":
    raise SystemExit(solve())
