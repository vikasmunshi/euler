#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 34: Digit Factorials [Level 0]. """
from __future__ import annotations

import itertools

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Enumerate digit multisets (order-independent factorial sums) via combinations-with-replacement
    over lengths 2..7, since no candidate exceeds 7 digits; O(sum_k C(k+9, k)) candidate checks."""
    upper_bound_num_digits = 7 + 1
    factorial = {"0": 1, "1": 1, "2": 2, "3": 6, "4": 24, "5": 120, "6": 720, "7": 5040, "8": 40320, "9": 362880}
    return str(sum(
        (
            int(num)
            for num_digits in range(2, upper_bound_num_digits)
            for digits in itertools.combinations_with_replacement("0123456789", num_digits)
            for num in (str(sum((factorial[d] for d in digits))),)
            if len(num) == num_digits
            and all((digit in num for digit in digits))
            and (num == str(sum((factorial[n] for n in num))))
        )
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
