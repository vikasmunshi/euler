#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=3
The prime factors of 13195 are 5, 7, 13 and 29.

What is the largest prime factor of the number 600851475143 ?
Answer: 6857
"""


def largest_prime_factor(number: int) -> int:
    def reduce(num: int, divisor: int) -> int:
        num //= divisor
        while num % divisor == 0:
            num //= divisor
        return num

    number, last_factor = (reduce(number, 2), 2) if number % 2 == 0 else (number, 1)
    factor, max_factor = 3, int(number ** 0.5)
    while number > 1 and factor < max_factor:
        if number % factor == 0:
            number, last_factor = reduce(number, factor), factor
            max_factor = int(number ** 0.5)
        factor += 2

    return last_factor if number == 1 else number


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog(timeout=10) as wd:
        result = wd.evaluate_range(largest_prime_factor, answers={13195: 29, 600851475143: 6857})
