#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 38: Pandigital Multiples [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def is_nine_pandigital(n: int) -> bool:
    """True iff n uses each digit 1-9 exactly once (a 1-to-9 pandigital); O(d) frequency array."""
    if n < 100000000 or n > 999999999:
        return False
    digits: list[int] = [0] * 10
    while n:
        d = n % 10
        if d == 0 or digits[d] == 1:
            return False
        digits[d] = 1
        n //= 10
    return sum(digits[1:]) == 9


@runner.main
def solve(*args: str) -> str:
    """Bounded brute force: 9 output digits with n > 1 caps x at 4 digits, so a static (n, max_x)
    table enumerates every case; scanning x downward makes the first pandigital hit the largest;
    O(X_max)."""
    for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)):
        while x > 0:
            number: int = int("".join([str(i * x) for i in range(1, n + 1)]))
            if is_nine_pandigital(number):
                return str(number)
            x -= 1
    raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
