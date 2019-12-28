#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=39
If p is the perimeter of a right angle triangle with integral length sides, {a,b,c},
there are exactly three solutions for p = 120.

{20,48,52}, {24,45,51}, {30,40,50}

For which value of p ≤ 1000, is the number of solutions maximised?
Answer: 840
"""
from collections import Counter
from math import gcd


def integer_right_triangles(max_perimeter: int) -> int:
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append(perimeter := 2 * m * (m + n))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


if __name__ == '__main__':
    from .evaluate import Watchdog

    answers = {100: 60, 1000: 840, 10000: 5040, 100000: 55440}
    with Watchdog() as wd:
        results = wd.evaluate_range(integer_right_triangles, answers=answers)
