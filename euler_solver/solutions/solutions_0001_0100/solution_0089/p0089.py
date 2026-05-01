#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 89: Roman Numerals.

Problem Statement:
    For a number written in Roman numerals to be considered valid there are basic
    rules which must be followed. Even though the rules allow some numbers to be
    expressed in more than one way there is always a "best" way of writing a
    particular number.

    For example, it would appear that there are at least six ways of writing the
    number sixteen:

        IIIIIIIIIIIIIIII
        VIIIIIIIIIIII
        VVIIIIII
        XIIIII
        VVVI
        XVI

    However, according to the rules only XIIIII and XVI are valid, and the last
    example is considered to be the most efficient, as it uses the least number
    of numerals.

    The 11K text file, roman.txt, contains one thousand numbers written in valid,
    but not necessarily minimal, Roman numerals; see About... Roman Numerals for
    the definitive rules for this problem.

    Find the number of characters saved by writing each of these in their minimal
    form.

    Note: You can assume that all the Roman numerals in the file contain no more
    than four consecutive identical units.

Solution Approach:
    Parse each Roman numeral and compute its integer value using traditional numeral
    interpretation. Re-encode the integer in the minimal Roman numeral form using
    established minimal rules (such as subtractive notation). Sum differences in
    length for all numerals. Efficiency stems from fast parsing and re-encoding.
    Complexity is O(n) for n numerals, with simple string operations.

Answer: 743
URL: https://projecteuler.net/problem=89
"""
from __future__ import annotations

from typing import Any, Dict

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 89
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0089_roman.txt'},
     'answer': 743},
]

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
    bits = []
    while number:
        # Find the largest value in the numeral dictionary that doesn't exceed the remaining number
        next_value, next_numeral = max((value, numeral) for value, numeral in numerals.items() if value <= number)
        number -= next_value
        bits.append(next_numeral)
    return ''.join(bits)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_roman_numerals_p0089_s0(*, file_url: str) -> int:
    characters_saved: int = 0
    for numeral in get_text_file(file_url).splitlines(keepends=False):
        minimal_form = number_as_roman_numeral(roman_to_number(numeral))
        characters_saved += len(numeral) - len(minimal_form)
    return characters_saved


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
