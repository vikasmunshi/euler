#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Word to Number Conversion"""
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
    return sum(ord(c) - 64 for c in word.strip('"') if c != ' ')
