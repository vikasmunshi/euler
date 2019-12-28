#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=36
The decimal number, 585 = 10010010012 (binary), is palindromic in both bases.

Find the sum of all numbers, less than one million, which are palindromic in base 10 and base 2.

(Please note that the palindromic number, in either base, may not include leading zeros.)
Answer: 872187
"""
from typing import Generator


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]:
    for digit in range(1, 10):
        yield digit
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)
        yield int(digits_str + digits_rev)
        if 2 * num_digits < max_digits:
            for mid_digit in '0123456789':
                yield int(digits_str + mid_digit + digits_rev)


def solution(max_digits: int) -> int:
    return sum(number for number in generate_decimal_palindromes(max_digits)
               if number == int(str(bin(number))[2:][::-1], base=2))


if __name__ == '__main__':
    from .evaluate import Watchdog

    answers = {1: 25, 2: 157, 3: 1772, 4: 18228, 6: 872187, 9: 2609044274}
    with Watchdog() as wd:
        results = wd.evaluate_range(func=solution, answers=answers)
