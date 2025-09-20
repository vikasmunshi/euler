#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 4: Largest Palindrome Product.

Problem Statement:
    A palindromic number reads the same both ways. The largest palindrome made
    from the product of two 2-digit numbers is 9009 = 91 × 99.

    Find the largest palindrome made from the product of two 3-digit numbers.

Solution Approach:
    Use brute force search over all products of two 3-digit numbers.
    Check if the product is a palindrome by string reversal.
    Track and return the maximum palindrome found.
    This is a straightforward nested loop approach with O(n^2) complexity,
    where n is the number of candidate digits (900 for 3-digit numbers).

Answer: 906609
URL: https://projecteuler.net/problem=4
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 4
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': 9009},
    {'category': 'main', 'input': {'n': 3}, 'answer': 906609},
    {'category': 'extra', 'input': {'n': 4}, 'answer': 99000099},
    {'category': 'extra', 'input': {'n': 5}, 'answer': 9966006699},
]


def is_palindromic(*, number: int) -> bool:
    str_number: str = str(number)
    return str_number == ''.join(reversed(str_number))


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_largest_palindrome_product_p0004_s0(*, n: int) -> int:
    largest_palindrome: int = 0
    a_max: int = 0
    b_max: int = 0
    max_number: int = 10 ** n - 1
    min_number: int = 10 ** (n - 1)
    max_multiple_11 = max_number - max_number % 11
    for a in range(max_number, min_number, -1):
        a_is_multiple_11 = a % 11 == 0
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            ab = a * b
            if ab <= largest_palindrome:
                break
            if is_palindromic(number=ab):
                a_max, b_max, largest_palindrome = (a, b, ab)
    if show_solution():
        print(f'Largest palindrome that is a multiple of two {n}-digit numbers is '
              f'{largest_palindrome} ({a_max}x{b_max})')
    return largest_palindrome


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
