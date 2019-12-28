#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=4
A palindromic number reads the same both ways. The largest palindrome made from the product of two 2-digit numbers is
9009 = 91 × 99.

Find the largest palindrome made from the product of two 3-digit numbers.
Answer: 906609
"""


def largest_palindrome_product(size: int) -> int:
    def is_palindromic(number: int) -> bool:
        number = str(number)
        return number == ''.join(reversed(number))

    largest_palindrome = 0
    max_number = 10 ** size - 1
    min_number = 10 ** (size - 1)
    max_multiple_11 = max_number - (max_number % 11)
    for a in range(max_number, min_number, -1):
        a_is_multiple_11 = a % 11 == 0
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            n = a * b
            if n <= largest_palindrome:
                break
            if is_palindromic(n):
                largest_palindrome = n

    return largest_palindrome


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog(timeout=10) as wd:
        result = wd.evaluate_range(largest_palindrome_product, answers={2: 9009, 3: 906609})
