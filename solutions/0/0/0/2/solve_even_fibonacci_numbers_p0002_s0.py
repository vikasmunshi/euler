#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0002/p0002.py
  func: solve_even_fibonacci_numbers_p0002_s0
"""

from __future__ import annotations

from sys import argv
from typing import Generator


def solve(*, max_limit: int) -> int:

    def _even_fibonacci_numbers() -> Generator[int, None, None]:
        even_fib_a, even_fib_b = (2, 8)
        while even_fib_a < max_limit:
            yield even_fib_a
            even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)

    return sum(_even_fibonacci_numbers())


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
