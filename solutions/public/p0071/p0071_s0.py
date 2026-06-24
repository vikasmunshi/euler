#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 71: Ordered Fractions [Level 2]. """
from __future__ import annotations

import fractions

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Farey neighbour of 3/7 in F_N: the immediate left fraction is 3/7 - 1/(7k) with
    k = floor(N/7), the largest denominator multiple of 7 within the bound; O(1).
    fractions.Fraction reduces the result automatically."""
    max_d = runner.parse_int(args[0])

    result: fractions.Fraction = fractions.Fraction(3, 7) - fractions.Fraction(1, 7 * (max_d // 7))
    if runner.show:
        difference = fractions.Fraction(3, 7) - result
        print(f"Solution for max_d={max_d!r}: "
              f"result={result!r} "
              f"difference={difference!r} "
              f"result.numerator={result.numerator!r}")
    return str(result.numerator)


if __name__ == "__main__":
    raise SystemExit(solve())
