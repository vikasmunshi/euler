#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 16: Power Digit Sum [Level 0]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum the decimal digits of base**power, computed with Python's built-in
    arbitrary-precision integers; an O(D) pass over its D ~ power*log10(base) digits."""
    base = runner.parse_int(args[0])
    power = runner.parse_int(args[1])

    return str(sum((int(i) for i in str(base**power))))


if __name__ == "__main__":
    raise SystemExit(solve())
