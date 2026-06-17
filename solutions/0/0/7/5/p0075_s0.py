#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 75: Singular Integer Right Triangles [Level 5]. """
from __future__ import annotations

import math
import typing

from solver.runners import runner


def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> typing.Generator[int, None, None]:
    """Yield every Pythagorean-triangle perimeter <= max_perimeter via Euclid's formula.

    Each primitive triple comes from a unique (m, n) with m > n > 0, gcd(m, n) = 1, opposite
    parity (enforced by starting n at m%2+1 and stepping by 2); its perimeter is 2m(m + n), and
    multiples k*p cover the non-primitive triples.
    """
    for m in range(2, int((max_perimeter / 2) ** 0.5)):
        for n in range(m % 2 + 1, m, 2):
            if math.gcd(m, n) != 1:
                continue
            p, k = (2 * m * (m + n), 1)
            while (perimeter := (k * p)) <= max_perimeter:
                yield perimeter
                k += 1


@runner.main
def solve(*args: str) -> str:
    """Sieve perimeters from Euclid's formula and count those reachable exactly once; O(L log L)."""
    max_perimeter = runner.parse_int(args[0])

    perimeter_count: dict[int, int] = {}
    for perimeter in gen_pythagorean_triangle_perimeters(max_perimeter=max_perimeter):
        perimeter_count[perimeter] = perimeter_count.get(perimeter, 0) + 1
    return str(sum((count == 1 for count in perimeter_count.values())))


if __name__ == "__main__":
    raise SystemExit(solve())
