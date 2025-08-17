#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 17: Number Letter Counts.

Problem Statement:
    If the numbers 1 to 5 are written out in words: one, two, three, four, five,
    then there are 3 + 3 + 5 + 4 + 4 = 19 letters used in total.

    If all the numbers from 1 to 1000 (one thousand) inclusive were written out
    in words, how many letters would be used?

    NOTE:
    Do not count spaces or hyphens. For example, 342 (three hundred and forty-two)
    contains 23 letters and 115 (one hundred and fifteen) contains 20 letters.
    The use of "and" when writing out numbers is in compliance with British usage.

Solution Approach:
    Count letters by converting each number to its British English word form,
    including the appropriate use of "and". Sum the lengths excluding spaces
    and hyphens. Use precomputed word lengths for efficiency. Complexity is O(N).

Answer: ...
URL: https://projecteuler.net/problem=17
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 17
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_number': 5}},
    {'category': 'main', 'input': {'max_number': 1000}}
]

number_to_word: dict[int, str] = {
    0: '',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    11: 'eleven',
    12: 'twelve',
    13: 'thirteen',
    14: 'fourteen',
    15: 'fifteen',
    16: 'sixteen',
    17: 'seventeen',
    18: 'eighteen',
    19: 'nineteen',
    20: 'twenty',
    30: 'thirty',
    40: 'forty',
    50: 'fifty',
    60: 'sixty',
    70: 'seventy',
    80: 'eighty',
    90: 'ninety',
}
placeholder_suffixes: tuple[str, ...] = (
    '',
    'thousand',
    'million',
    'billion',
    'trillion',
    'quadrillion',
    'quintillion',
    'sextillion',
    'septillion',
    'octillion',
    'nonillion',
    'decillion',
    'undecillion',
    'duodecillion',
    'tredecillion',
    'quatttuor-decillion',
    'quindecillion',
    'sexdecillion',
    'septen-decillion',
    'octodecillion',
    'novemdecillion',
    'vigintillion',
    'centillion',
)
hundred_suffix: str = 'hundred'


@lru_cache()
def number_triplet_in_words(number: int) -> str:
    ...

def convert_number_to_words(number: int) -> str:
    ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_number_letter_counts_p0017_s0(*, max_number: int) -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
