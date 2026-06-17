#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 30: Digit Fifth Powers [Level 0]. """
from __future__ import annotations

import itertools
import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Enumerate sorted digit multisets (the digit-power sum is order-independent), capped at
    ceil(log10(n*9^n)) digits since no longer number can reach its own digit-power sum, and keep
    those whose sum reproduces itself; O(C(10+k-1, k) * k) for k digits."""
    n = runner.parse_int(args[0])

    upper_bound_num_digits = math.ceil(math.log(n * 9**n, 10))
    return str(sum(
        (
            num
            for digits in itertools.combinations_with_replacement(range(10), upper_bound_num_digits)
            if (num := sum((x**n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))
        )
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
