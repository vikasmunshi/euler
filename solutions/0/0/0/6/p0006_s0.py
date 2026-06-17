#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 6: Sum Square Difference [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Closed form: triangular-number square minus square-pyramidal sum, S(n)**2 - SS(n); O(1)."""
    n = runner.parse_int(args[0])

    return str((n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6)


if __name__ == "__main__":
    raise SystemExit(solve())
