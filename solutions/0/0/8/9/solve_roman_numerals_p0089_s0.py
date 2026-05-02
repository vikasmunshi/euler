#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0089/p0089.py
  func: solve_roman_numerals_p0089_s0
"""

from __future__ import annotations

from pathlib import Path
from sys import argv
from typing import Dict


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


values: Dict[str, int] = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_number(numeral: str) -> int:
    value, last = (0, 0)
    for r in reversed(numeral):
        n = values[r]
        if last > n:
            value -= n
        else:
            value += n
        last = n
    return value


numerals: Dict[int, str] = {
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
    bits = []
    while number:
        next_value, next_numeral = max(((value, numeral) for value, numeral in numerals.items() if value <= number))
        number -= next_value
        bits.append(next_numeral)
    return "".join(bits)


def solve(*, file_url: str) -> int:
    characters_saved: int = 0
    for numeral in get_text_file(file_url).splitlines(keepends=False):
        minimal_form = number_as_roman_numeral(roman_to_number(numeral))
        characters_saved += len(numeral) - len(minimal_form)
    return characters_saved


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
