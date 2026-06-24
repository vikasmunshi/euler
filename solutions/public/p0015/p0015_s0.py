#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 15: Lattice Paths [Level 1]. """
from __future__ import annotations

import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Closed-form central binomial coefficient: n×n grid paths = C(2n, n) = (2n)!/(n!)²; O(n) big-int mults."""
    lattice_size = runner.parse_int(args[0])

    return str(math.factorial(2 * lattice_size) // math.factorial(lattice_size) ** 2)


if __name__ == "__main__":
    raise SystemExit(solve())
