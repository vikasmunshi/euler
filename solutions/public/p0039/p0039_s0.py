#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 39: Integer Right Triangles [Level 1]. """
from __future__ import annotations

import collections
import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Enumerate primitive Pythagorean triples via Euclid's formula (primitive
    perimeter p0 = 2m(m + n) for coprime m > n of opposite parity), record p0
    and every multiple, then take the most common perimeter. O(P log P)."""
    max_perimeter = runner.parse_int(args[0])

    # Loop bounds invert p0 = 2m(m + n) <= max_perimeter to closed form; the
    # inner step of 2 keeps m and n of opposite parity, and gcd(m, n) == 1
    # keeps only primitive triples.
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter**0.5) - 6) // 8, 1):
        for m in (
            m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if math.gcd(m, n) == 1
        ):
            triangle_perimeters.append((perimeter := (2 * m * (m + n))))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return str(collections.Counter(triangle_perimeters).most_common()[0][0])


if __name__ == "__main__":
    raise SystemExit(solve())
