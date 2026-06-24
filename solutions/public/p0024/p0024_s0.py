#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 24: Lexicographic Permutations [Level 1]. """
from __future__ import annotations

import math

from solver.runners import runner


def recursive_solution(digits: str, permutation_number: int) -> str:
    """Return the 1-based permutation_number-th lexicographic permutation of the sorted digits."""
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, math.factorial(len(digits) - 1))
    result: str = digits[current] + recursive_solution(
        digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1
    )
    return result


@runner.main
def solve(*args: str) -> str:
    """Recursive unranking via the factorial number system: at each step divmod the 0-based
    rank by (len-1)! to pick the leading digit, then recurse on the remainder; O(n^2)."""
    digits = args[0]
    permutation_number = runner.parse_int(args[1])

    return str(recursive_solution(digits=digits, permutation_number=permutation_number))


if __name__ == "__main__":
    raise SystemExit(solve())
