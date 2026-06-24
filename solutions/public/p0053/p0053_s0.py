#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 53: Combinatoric Selections [Level 1]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Count C(n, r) above the threshold by walking each Pascal row with the recurrence
    C(n, r+1) = C(n, r) * (n - r) / (r + 1). Rows are unimodal and symmetric, so the first r that
    exceeds the threshold makes entries r..n-r qualify; add n - 2*r + 1 and stop. O(max_n^2) worst
    case, far less with the early exit."""
    max_n = runner.parse_int(args[0])
    threshold = runner.parse_int(args[1])

    count = 0
    for n in range(1, max_n + 1):
        c = 1
        for r in range(0, n // 2 + 1):
            if c > threshold:
                count += n - 2 * r + 1
                break
            else:
                c = c * (n - r) // (r + 1)
    return str(count)


if __name__ == "__main__":
    raise SystemExit(solve())
