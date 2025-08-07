#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 75: Singular Integer Right Triangles.

  Problem Statement:
    It turns out that 12 cm is the smallest length of wire that can be bent
    to form an integer sided right angle triangle in exactly one way, but
    there are many more examples.

    12 cm: (3, 4, 5)
    24 cm: (6, 8, 10)
    30 cm: (5, 12, 13)
    36 cm: (9, 12, 15)
    40 cm: (8, 15, 17)
    48 cm: (12, 16, 20)

    In contrast, some lengths of wire, like 20 cm, cannot be bent to form an
    integer sided right angle triangle, and other lengths allow more than
    one solution to be found; for example, using 120 cm it is possible to
    form exactly three different integer sided right angle triangles.

    120 cm: (30, 40, 50), (20, 48, 52), (24, 45, 51)

    Given that L is the length of the wire, for how many values of L <=
    1,500,000 can exactly one integer sided right angle triangle be formed?

  Solution Approach:
    To solve this problem, generate all primitive Pythagorean triples using the
    Euclid's formula, which uses pairs of integers (m, n) with m > n > 0 to
    produce triples (a, b, c). For each primitive triple, also consider its
    multiples, since non-primitive triples correspond to scaled versions of
    primitive ones.

    Keep track of the perimeter lengths that can form right angle triangles. Use
    an array or dictionary to count how many triples correspond to each
    possible perimeter length up to 1,500,000.

    Finally, count how many perimeter values have exactly one corresponding right
    triangle. This involves efficient iteration and sieve-like marking to avoid
    excessive computations.

  Test Cases:
    preliminary:
      max_perimeter=50,
      answer=6.

    main:
      max_perimeter=1500000,
      answer=161667.

    extended:
      max_perimeter=10000000,
      answer=1067080.


  Answer: 161667
  URL: https://projecteuler.net/problem=75
"""
from __future__ import annotations

from math import gcd
from typing import Dict, Generator

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=75, test_case_category=TestCaseCategory.EXTENDED)
def singular_integer_right_triangles(*, max_perimeter: int) -> int:
    perimeter_count: Dict[int, int] = {}
    for perimeter in gen_pythagorean_triangle_perimeters(max_perimeter=max_perimeter):
        perimeter_count[perimeter] = perimeter_count.get(perimeter, 0) + 1
    return sum((count == 1 for count in perimeter_count.values()))


def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> Generator[int, None, None]:
    for m in range(2, int((max_perimeter / 2) ** 0.5)):
        for n in range(m % 2 + 1, m, 2):
            if gcd(m, n) != 1:
                continue
            p, k = (2 * m * (m + n), 1)
            while (perimeter := (k * p)) <= max_perimeter:
                yield perimeter
                k += 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=75, time_out_in_seconds=300, mode='evaluate'))
