#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 2: Even Fibonacci Numbers [Level 0]. """
from __future__ import annotations

import typing

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sum the even Fibonacci numbers below max_limit using the closed recurrence
    E(k+1) = 4*E(k) + E(k-1) on even terms only (every third Fibonacci term is
    even); O(log max_limit) time, O(1) space."""
    max_limit = runner.parse_int(args[0])

    def _even_fibonacci_numbers() -> typing.Generator[int, None, None]:
        """Yield successive even Fibonacci numbers below max_limit."""
        even_fib_a, even_fib_b = (2, 8)
        while even_fib_a < max_limit:
            yield even_fib_a
            even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)

    return str(sum(_even_fibonacci_numbers()))


if __name__ == "__main__":
    raise SystemExit(solve())
