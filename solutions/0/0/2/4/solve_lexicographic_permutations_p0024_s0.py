#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0024/p0024.py
  func: solve_lexicographic_permutations_p0024_s0
"""

from __future__ import annotations

from math import factorial
from sys import argv, setrecursionlimit


def recursive_solution(digits: str, permutation_number: int) -> str:
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))
    result: str = digits[current] + recursive_solution(
        digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1
    )
    return result


def solve(*, digits: str, permutation_number: int) -> str:
    return recursive_solution(digits=digits, permutation_number=permutation_number)


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(digits=str(argv[1]), permutation_number=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
