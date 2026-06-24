#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 52: Permuted Multiples [Level 0]. """
from __future__ import annotations

import sys

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Linear scan: x is the answer when 1x..Mx share one sorted-digit fingerprint, so the set of
    fingerprints has size 1. The digit-count constraint keeps the scan short. O(N * M * D)."""
    multiples = runner.parse_int(args[0])

    if not (isinstance(multiples, int) and 1 < multiples < 7):
        raise ValueError("multiples must be an integer between 2 and 6, both inclusive.")
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):
        if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return str(i)
    else:
        raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
