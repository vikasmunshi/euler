#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" """
from functools import lru_cache


@lru_cache(maxsize=None)
def sum_digits(n: int | str) -> int:
    """Calculate the sum of all digits in a given number.

    This function converts a number to a string, then sums its individual digits.
    Commonly used in Project Euler problems that require digit manipulation.
    Accepts either integer or string input for flexibility.

    This function is used in problems like #65 (Convergents of e) and #80 (Square root digital expansion).

    Args:
        n: An integer or string whose digits need to be summed

    Returns:
        The sum of all digits in the input number

    Examples:
        >>> sum_digits(123)
        6  # 1 + 2 + 3 = 6
        >>> sum_digits(999)
        27  # 9 + 9 + 9 = 27
        >>> sum_digits(123)
        6  # Works with string input too
    """
    if isinstance(n, str):
        n = int(n) if n else 0
    if n < 0:
        return sum_digits(-n)
    return sum(int(digit) for digit in str(n))
