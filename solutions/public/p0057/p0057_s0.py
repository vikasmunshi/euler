#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 57: Square Root Convergents [Level 2]. """
from __future__ import annotations

import sys

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Iterate the sqrt(2) convergent recurrence (p, q) -> (p + 2q, p + q) with exact
    big integers, counting steps where the numerator has more decimal digits than the
    denominator; O(n^2) from adding linearly growing big integers."""
    expansions = runner.parse_int(args[0])

    numerator, denominator, result = (1, 1, 0)
    for _ in range(expansions):
        numerator, denominator = (numerator + 2 * denominator, numerator + denominator)
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            # Python 3.11+ caps int-to-str conversion; lift it only when it actually fires.
            sys.set_int_max_str_digits(0)
            print(f"sys.set_int_max_str_digits(0) expansions={expansions!r}, "
                  f"len(str(numerator))={len(str(numerator))!r}, "
                  f"len(str(denominator))={len(str(denominator))!r}")
            result += len(str(numerator)) > len(str(denominator))
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
