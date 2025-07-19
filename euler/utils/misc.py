#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Miscellaneous utility functions used across Project Euler solutions.

This module provides commonly used helper functions for Project Euler problems,
including word-to-number conversion and digit manipulation utilities.
"""
from functools import lru_cache


@lru_cache(maxsize=None)
def word_to_num(word: str) -> int:
    """Convert a word to a number by summing the alphabetical position values of each letter.

    Each letter is assigned a value based on its position in the alphabet (A=1, B=2, etc.).
    Used in Project Euler problems where alphabetical values of words are needed.
    The function automatically strips any surrounding double quotes from the input word.

    This function is used in problems like #22 (Name scores) and #42 (Coded triangle numbers).

    Args:
        word: The input word (expected to be uppercase letters)

    Returns:
        The sum of the alphabetical positions of all letters in the word

    Examples:
        >>> word_to_num('COLIN')
        53  # C(3) + O(15) + L(12) + I(9) + N(14) = 53
        >>> word_to_num('"COLIN"')  # With quotes that get stripped
        53
    """
    return sum(ord(c) - 64 for c in word.strip('"'))


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
        >>> sum_digits('123')
        6  # Works with string input too
    """
    return sum(int(digit) for digit in str(n))
