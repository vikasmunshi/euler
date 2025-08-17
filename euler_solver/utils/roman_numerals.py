#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roman Numerals Module

This module provides utilities for converting between Roman numerals and decimal integers.
It handles standard Roman numeral notation including subtractive combinations (IV, IX, etc.).

Two main functions are provided:
- roman_to_number: Converts a Roman numeral string to an integer
- number_as_roman_numeral: Converts an integer to its minimal Roman numeral representation
"""

from typing import Dict

# Mapping of individual Roman numeral characters to their decimal values
values: Dict[str, int] = {
    'I': 1,  # Unus
    'V': 5,  # Quinque
    'X': 10,  # Decem
    'L': 50,  # Quinquaginta
    'C': 100,  # Centum
    'D': 500,  # Quingenti
    'M': 1000,  # Mille
}

# Mapping of decimal values to their Roman numeral representations
# Includes subtractive combinations (IV, IX, etc.) for minimal representation
numerals: Dict[int, str] = {
    # Units
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX',
    # Tens
    10: 'X', 20: 'XX', 30: 'XXX', 40: 'XL', 50: 'L', 60: 'LX', 70: 'LXX', 80: 'LXXX', 90: 'XC',
    # Hundreds
    100: 'C', 200: 'CC', 300: 'CCC', 400: 'CD', 500: 'D', 600: 'DC', 700: 'DCC', 800: 'DCCC', 900: 'CM',
    # Thousands
    1000: 'M',
}


def roman_to_number(numeral: str) -> int:
    """
    Convert a Roman numeral string to its corresponding decimal integer value.

    This function implements the standard Roman numeral reading rules, including
    the subtractive notation where a smaller value before a larger one means
    subtraction (e.g., IV = 4, IX = 9).

    The algorithm processes the string from right to left, comparing each numeral
    with the previous one to determine whether to add or subtract its value.

    Args:
        numeral (str): A valid Roman numeral string (e.g., 'XIV', 'MCMXCIX')

    Returns:
        int: The decimal integer value of the Roman numeral

    Example:
        >>> roman_to_number('XIV')
        14
        >>> roman_to_number('MCMXCIX')
        1999
    """
    value, last = 0, 0
    for r in reversed(numeral):
        n = values[r]
        if last > n:
            value -= n  # Subtractive case (like IV, IX, etc.)
        else:
            value += n  # Standard additive case
        last = n
    return value


def number_as_roman_numeral(number: int) -> str:
    """
    Convert a decimal integer to its minimal Roman numeral representation.

    This function implements a greedy algorithm that repeatedly finds the largest
    Roman numeral value that can be subtracted from the remaining number. This
    approach ensures the minimal (most efficient) representation is generated.

    The function handles the standard Roman numeral notation including subtractive
    combinations (IV, IX, XL, etc.) that are defined in the numerals dictionary.

    Args:
        number (int): A positive integer to convert (should be > 0)

    Returns:
        str: The minimal Roman numeral representation of the number

    Example:
        >>> number_as_roman_numeral(14)
        'XIV'
        >>> number_as_roman_numeral(1999)
        'MCMXCIX'
    """
    bits = []
    while number:
        # Find the largest value in the numerals dictionary that doesn't exceed the remaining number
        next_value, next_numeral = max((value, numeral) for value, numeral in numerals.items() if value <= number)
        number -= next_value
        bits.append(next_numeral)
    return ''.join(bits)
