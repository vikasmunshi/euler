#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=23
A perfect number is a number for which the sum of its proper divisors is exactly equal to the number. For example,
the sum of the proper divisors of 28 would be 1 + 2 + 4 + 7 + 14 = 28, which means that 28 is a perfect number.

A number n is called deficient if the sum of its proper divisors is less than n and it is called abundant if this
sum exceeds n.

As 12 is the smallest abundant number, 1 + 2 + 3 + 4 + 6 = 16, the smallest number that can be written as the sum of two
abundant numbers is 24. By mathematical analysis, it can be shown that all integers greater than 28123 can be written as
the sum of two abundant numbers. However, this upper limit cannot be reduced any further by analysis even though it is
known that the greatest number that cannot be expressed as the sum of two abundant numbers is less than this limit.

Find the sum of all the positive integers which cannot be written as the sum of two abundant numbers.
Answer: 4179871
"""


def sum_non_abundant_numbers() -> int:
    def sum_proper_divisors(n: int) -> int:
        n_sqrt = int(n ** 0.5)
        return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)

    abundant_numbers = [i for i in range(12, 28123 - 12) if sum_proper_divisors(i) > i]
    abundant_sums = (a + b for a in abundant_numbers for b in abundant_numbers)
    return sum(set(range(1, 28123 + 1)) - set(abundant_sums))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate(sum_non_abundant_numbers)(answer=4179871)
