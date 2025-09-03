#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Pandigital Numbers"""
from __future__ import annotations

from itertools import permutations
from typing import Generator

nine_digits: tuple[str, ...] = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
zero_to_nine: tuple[str, ...] = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
set_nine_digits: set[str] = set(nine_digits)
set_zero_to_nine: set[str] = set(zero_to_nine)


def gen_n_digit_pandigital_numbers(n: int, descending: bool = False) -> Generator[int, None, None]:
    assert 1 <= n <= 9, 'n must be between 1 and 9'
    n_digits: tuple[str, ...] = nine_digits[:n]
    if descending:
        n_digits = n_digits[::-1]
    yield from (int(''.join(digits)) for digits in permutations(n_digits, n))


def gen_zero_to_nine_pandigital_numbers(descending: bool = False) -> Generator[str, None, None]:
    n_digits: tuple[str, ...] = zero_to_nine
    if descending:
        n_digits = n_digits[::-1]
    yield from (''.join(digits) for digits in permutations(n_digits) if digits[0] != '0')


def is_n_digit_pandigital(num: int) -> bool:
    n: int = len(str(num))
    return 1 < n < 9 and set(str(num)) == set(nine_digits[:n])


def is_nine_pandigital(n: int | str) -> bool:
    return len(str(n)) == 9 and set(str(n)) == set_nine_digits


def is_zero_to_nine_pandigital(n: int | str) -> bool:
    return len(str(n)) == 10 and set(str(n)) == set_zero_to_nine
