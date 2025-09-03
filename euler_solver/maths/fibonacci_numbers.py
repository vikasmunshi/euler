#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fibonacci numbers utilities

Helpers for generating Fibonacci sequences and computing properties often used in
Project Euler problems. Includes fast closed forms for the k-th value, the
leading digits, and the number of digits, plus generators for plain and modular
sequences.

Public API
- gen_fibonacci(max_num=float('inf')): yield Fibonacci numbers up to max_num
  (inclusive). Infinite when max_num is infinity.
- gen_fibonacci_modulo_n(n): yield an infinite sequence of Fibonacci numbers
  reduced modulo n.
- k_th_fibonacci_number(k): return the k-th Fibonacci number (with F1=1, F2=1).
- most_significant_n_digits_of_k_th_fibonacci_number(k, n): return the first n
  digits of F_k (accurate for 0 < n < 13).
- number_of_digits_in_k_th_fibonacci_number(k): return the decimal digit count
  of F_k.

Constants
- sqrt_5: Precomputed square root of 5.
- phi: Golden ratio (1 + sqrt(5)) / 2.
- log10_sqrt_5: Base-10 logarithm of sqrt(5).
- log10_phi: Base-10 logarithm of phi.

Examples
>>> from euler_solver.maths.fibonacci_numbers import gen_fibonacci, k_th_fibonacci_number
>>> list(gen_fibonacci(10))
[1, 1, 2, 3, 5, 8]
>>> k_th_fibonacci_number(10)
55
"""
from __future__ import annotations

from math import floor, log10, sqrt
from typing import Generator

sqrt_5: float = sqrt(5)
phi: float = (1 + sqrt_5) / 2
log10_sqrt_5: float = log10(sqrt_5)
log10_phi: float = log10(phi)


def gen_fibonacci(max_num: int | float = float('inf')) -> Generator[int, None, None]:
    """
    Generate Fibonacci numbers up to a maximum value.

    The sequence uses the convention F1=1, F2=1 and proceeds with F_{k+2}=F_{k+1}+F_k.
    When max_num is infinity (the default), the generator is infinite; otherwise it
    yields values ≤ max_num.

    Args:
        max_num (int | float): Upper bound (inclusive). Must be non-negative. Use
            float('inf') to generate indefinitely.

    Yields:
        int: Next Fibonacci number in the sequence.

    Raises:
        ValueError: If max_num is negative.
    """
    if max_num < 0:
        raise ValueError("max_num must be non-negative.")

    a, b = 1, 1
    while a <= max_num:
        yield a
        a, b = b, a + b


def gen_fibonacci_modulo_n(n: int) -> Generator[int, None, None]:
    """
    Generate an infinite Fibonacci sequence reduced modulo n.

    Uses F1=1, F2=1. Each yielded value is in the range [0, n-1].

    Args:
        n (int): Modulus. Must be greater than 0.

    Yields:
        int: Next Fibonacci value modulo n.

    Raises:
        ValueError: If n <= 0.
    """
    if n <= 0:
        raise ValueError("n must be greater than 0.")

    a, b = 1, 1
    while True:
        yield a
        a, b = b, (a + b) % n


def k_th_fibonacci_number(k: int) -> int:
    """
    Return the k-th Fibonacci number using a closed form (Binet’s formula).

    Uses the convention F1=1, F2=1 and rounds to the nearest integer.

    Args:
        k (int): 1-based index in the Fibonacci sequence. Must be ≥ 1.

    Returns:
        int: The value F_k.

    Raises:
        ValueError: If k < 1.
    """
    if k < 1:
        raise ValueError("k must be greater than or equal to 1.")

    return floor(phi ** k / 5 ** 0.5 + 0.5)


def most_significant_n_digits_of_k_th_fibonacci_number(k: int, n: int) -> int:
    """
    Return the first n digits of the k-th Fibonacci number.

    Accuracy note: this leading-digits formula is accurate for 0 < n < 13.

    Args:
        k (int): 1-based index of the Fibonacci number. Must be ≥ 1.
        n (int): Number of leading digits to return. Must satisfy 0 < n < 13.

    Returns:
        int: The most significant n digits of F_k.

    Raises:
        ValueError: If k < 1.
        AssertionError: If n is not within 0 < n < 13.
    """
    if k < 1:
        raise ValueError("k must be greater than or equal to 1.")
    assert 0 < n < 13, 'formula results are accurate only for n < 13'

    return floor(pow(10, (((k * log10_phi) - log10_sqrt_5) % 1) + (n - 1)))


def number_of_digits_in_k_th_fibonacci_number(k: int) -> int:
    """
    Return the number of decimal digits in the k-th Fibonacci number.

    Uses the closed-form relation floor(k*log10(phi) - log10(sqrt(5)) + 1).

    Args:
        k (int): 1-based index of the Fibonacci number. Must be ≥ 1.

    Returns:
        int: The count of digits of F_k in base 10.

    Raises:
        ValueError: If k < 1.
    """
    if k < 1:
        raise ValueError("k must be greater than or equal to 1.")

    return floor(k * log10_phi - log10_sqrt_5 + 1)
