#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 89: Roman Numerals [Level 4]. """
from __future__ import annotations

from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources/" + src.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


values: dict[str, int] = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


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


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(file_url=str(argv[1])))
