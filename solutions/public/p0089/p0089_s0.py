#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 89: Roman Numerals [Level 4]. """
from __future__ import annotations

from solver.runners import runner

values: dict[str, int] = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_number(numeral: str) -> int:
    """Parse a numeral to an integer by scanning right-to-left, subtracting any symbol smaller
    than the one to its right (the subtractive pairs); O(len)."""
    value, last = (0, 0)
    for r in reversed(numeral):
        n = values[r]
        if last > n:
            value -= n
        else:
            value += n
        last = n
    return value


numerals: dict[int, str] = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    20: "XX",
    30: "XXX",
    40: "XL",
    50: "L",
    60: "LX",
    70: "LXX",
    80: "LXXX",
    90: "XC",
    100: "C",
    200: "CC",
    300: "CCC",
    400: "CD",
    500: "D",
    600: "DC",
    700: "DCC",
    800: "DCCC",
    900: "CM",
    1000: "M",
}


def number_as_roman_numeral(number: int) -> str:
    """Encode an integer minimally by greedily taking the largest fitting denomination (including
    subtractive pairs), which yields the unique shortest numeral; O(len)."""
    bits = []
    while number:
        next_value, next_numeral = max(((value, numeral) for value, numeral in numerals.items() if value <= number))
        number -= next_value
        bits.append(next_numeral)
    return "".join(bits)


@runner.main
def solve(*args: str) -> str:
    """Convert each numeral to an integer and re-encode it minimally, summing the characters saved;
    O(N) over the N input lines, each numeral of bounded length."""
    file_url = args[0]

    characters_saved: int = 0
    for numeral in runner.get_text_file(file_url).splitlines(keepends=False):
        minimal_form = number_as_roman_numeral(roman_to_number(numeral))
        characters_saved += len(numeral) - len(minimal_form)
    return str(characters_saved)


if __name__ == "__main__":
    raise SystemExit(solve())
