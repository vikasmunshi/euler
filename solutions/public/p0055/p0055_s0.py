#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 55: Lychrel Numbers [Level 2]. """
from __future__ import annotations

from solver.runners import runner


def is_lychrel(*, number: int, max_iterations: int) -> bool:
    """True if no palindrome appears within max_iterations reverse-and-add steps; tests the result, not the seed."""
    for _ in range(max_iterations):
        number += int(str(number)[::-1])
        if str(number) == str(number)[::-1]:
            return False
    else:
        return True


@runner.main
def solve(*args: str) -> str:
    """Count Lychrel numbers up to max_limit via bounded big-integer reverse-and-add; O(max_limit * max_iterations)."""
    max_iterations = runner.parse_int(args[0])
    max_limit = runner.parse_int(args[1])

    return str(sum((is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1))))


if __name__ == "__main__":
    raise SystemExit(solve())
