#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Fibonacci Numbers"""
from __future__ import annotations

from math import floor, log10, sqrt
from typing import Generator

sqrt_5: float = sqrt(5)
phi: float = (1 + sqrt_5) / 2
log10_sqrt_5: float = log10(sqrt_5)
log10_phi: float = log10(phi)


def gen_fibonacci(max_num: int | float = float('inf')) -> Generator[int, None, None]:
    a, b = 1, 1
    while a <= max_num:
        yield a
        a, b = b, a + b


def gen_fibonacci_modulo_n(n: int) -> Generator[int, None, None]:
    a, b = 1, 1
    while True:
        yield a
        a, b = b, (a + b) % n


def k_th_fibonacci_number(k: int) -> int:
    return floor(phi ** k / 5 ** 0.5 + 0.5)


def most_significant_n_digits_of_k_th_fibonacci_number(k: int, n: int) -> int:
    return floor(pow(10, (((k * log10_phi) - log10_sqrt_5) % 1) + (n - 1)))


def number_of_digits_in_k_th_fibonacci_number(k: int) -> int:
    return floor(k * log10_phi - log10_sqrt_5 + 1)
