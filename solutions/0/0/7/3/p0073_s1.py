#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 73: Counting Fractions in a Range [Level 3]. """
from __future__ import annotations

import sys

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Stern-Brocot recursive mediant search of (1/3, 1/2): the mediant denominator is the sum of
    the boundary denominators; recurse into both halves while it stays within max_d. Only
    denominators are tracked. O(answer) time, O(depth) stack."""
    max_d = runner.parse_int(args[0])
    sys.setrecursionlimit(10 ** 6)

    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        """Count fractions in (lower, upper) via their mediant; 0 once the mediant exceeds max_d."""
        if (mediant := (lower_denominator + upper_denominator)) > max_d:
            return 0
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return str(recursion(lower_denominator=3, upper_denominator=2))


if __name__ == "__main__":
    raise SystemExit(solve())
