#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 91: Right Triangles with Integer Coordinates [Level 6]. """
from __future__ import annotations

import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Classify right triangles by the location of the right angle; O(N^2 log N).

    The origin contributes 3 * N^2 axis-aligned cases. For a right angle at non-origin P = (x, y),
    the primitive perpendicular step is (-y/m, x/m) with m = gcd(x, y); the reachable lattice points
    are bounded by horizontal room x*m/y and vertical room m*(N-y)/x, and the minimum counts them.
    Doubling covers the right angle at Q and the opposite direction; the gcd makes both divisions exact.
    """
    coordinate_limit = runner.parse_int(args[0])

    triangles_at_p_or_q = sum(
        (
            min(x * m // y, m * (coordinate_limit - y) // x)
            for x in range(1, coordinate_limit + 1)
            for y in range(1, coordinate_limit)
            for m in [math.gcd(x, y)]
        )
    )
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * coordinate_limit**2
    return str(triangles_at_p_or_q + triangles_at_origin)


if __name__ == "__main__":
    raise SystemExit(solve())
