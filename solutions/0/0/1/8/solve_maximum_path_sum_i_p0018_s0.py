#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0018/p0018.py
  func: solve_maximum_path_sum_i_p0018_s0
"""

from __future__ import annotations

from copy import deepcopy
from sys import argv
from typing import List

TRIANGLE_A = "3\n7 4\n2 4 6\n8 5 9 3\n"


def text2triangle(text: str) -> List[List[int]]:
    return [[int(num) for num in line.split(" ")] for line in text.splitlines() if line != ""]


TRIANGLE_B = (
    "75\n"
    "95 64\n"
    "17 47 82\n"
    "18 35 87 10\n"
    "20 04 82 47 65\n"
    "19 01 23 75 03 34\n"
    "88 02 77 73 07 63 67\n"
    "99 65 04 28 06 16 70 92\n"
    "41 41 26 56 83 40 80 70 33\n"
    "41 48 72 33 47 32 37 16 94 29\n"
    "53 71 44 65 25 43 91 52 97 51 14\n"
    "70 11 33 28 77 73 17 78 39 68 17 57\n"
    "91 71 52 38 17 14 91 43 58 50 27 29 48\n"
    "63 66 04 68 89 53 67 30 73 16 69 87 40 31\n"
    "04 62 98 27 23 09 70 98 73 93 38 53 60 04 23\n"
)


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


def solve(*, triangle_str: str) -> int:
    triangle_str = TRIANGLE_A if triangle_str == "TRIANGLE_A" else TRIANGLE_B if triangle_str == "TRIANGLE_B" else ""
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


def main() -> int:
    print(solve(triangle_str=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
