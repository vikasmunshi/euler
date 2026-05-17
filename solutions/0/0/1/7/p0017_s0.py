#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 17: Number Letter Counts [Level 2]. """
from __future__ import annotations

import functools
from sys import argv, stderr
from time import perf_counter
from typing import Any

placeholder_suffixes: tuple[str, ...] = (
    "",
    "thousand",
    "million",
    "billion",
    "trillion",
    "quadrillion",
    "quintillion",
    "sextillion",
    "septillion",
    "octillion",
    "nonillion",
    "decillion",
    "undecillion",
    "duodecillion",
    "tredecillion",
    "quatttuor-decillion",
    "quindecillion",
    "sexdecillion",
    "septen-decillion",
    "octodecillion",
    "novemdecillion",
    "vigintillion",
    "centillion",
)
number_to_word: dict[int, str] = {
    0: "",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}
hundred_suffix: str = "hundred"


@functools.lru_cache()
def number_triplet_in_words(number: int) -> str:
    number = int(number)
    if number in number_to_word:
        return number_to_word[number]
    elif number < 100:
        return f"{number_to_word[10 * (number // 10)]}-{number_to_word[number % 10]}"
    else:
        hundreds = number // 100
        rest = number % 100
        return f"{number_to_word[hundreds]} {hundred_suffix}{(' and ' if rest else '')}{number_triplet_in_words(rest)}"


def convert_number_to_words(number: int) -> str:
    number_triplets = f"{number:,}".split(",")
    len_number_triplets = len(number_triplets)
    number_triplet_strings = (
        (number_triplet_in_words(int(s)), placeholder_suffixes[len_number_triplets - i - 1])
        for i, s in enumerate(number_triplets)
    )
    number_triplets_in_words = list((f"{s}{(' ' if p else '')}{p}" for s, p in number_triplet_strings))
    if len_number_triplets > 1 and number_triplets_in_words[-1] and ("and" not in number_triplets_in_words[-1]):
        number_triplets_in_words[-1] = "and " + number_triplets_in_words[-1]
    return " ".join(number_triplets_in_words)


def solve(*, max_number: int) -> int:
    ignored_chars = {ord(i): None for i in (" ", "-")}
    return sum((len(convert_number_to_words(s).translate(ignored_chars)) for s in range(1, max_number + 1)))


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
    raise SystemExit(main(max_number=int(argv[1])))
