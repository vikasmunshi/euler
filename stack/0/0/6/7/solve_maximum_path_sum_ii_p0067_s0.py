#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0067/p0067.py
  func: solve_maximum_path_sum_ii_p0067_s0
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from sys import argv
from typing import List


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def text2triangle(text: str) -> List[List[int]]:
    return [[int(num) for num in line.split(" ")] for line in text.splitlines() if line != ""]


def solve(*, file_url: str) -> int:
    triangle_str: str = get_text_file(file_url)
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
