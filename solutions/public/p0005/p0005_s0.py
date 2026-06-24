#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 5: Smallest Multiple [Level 0]. """
from __future__ import annotations

import functools
import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Iterative LCM of 1..n, folded over the range with lcm(x, y) = x * y // gcd(x, y); O(n log n)."""
    n = runner.parse_int(args[0])

    return str(functools.reduce(lambda x, y: x * y // math.gcd(x, y), range(2, n + 1), 1))


if __name__ == "__main__":
    raise SystemExit(solve())
