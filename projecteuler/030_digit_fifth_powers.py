#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=30
Surprisingly there are only three numbers that can be written as the sum of fourth powers of their digits:
1634 = 1^4 + 6^4 + 3^4 + 4^4
8208 = 8^4 + 2^4 + 0^4 + 8^4
9474 = 9^4 + 4^4 + 7^4 + 4^4
As 1 = 1^4 is not a sum it is not included.

The sum of these numbers is 1634 + 8208 + 9474 = 19316.

Find the sum of all the numbers that can be written as the sum of fifth powers of their digits.
Answer: 443839
"""
from itertools import combinations_with_replacement
from math import ceil, log


def sum_digit_nth_power(n: int) -> int:
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum(
        num
        for digits in combinations_with_replacement(range(10), upper_bound_num_digits)
        for num in (sum(x ** n for x in digits),)
        if num > 9 and num == sum(int(x) ** n for x in str(num))
    )


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(sum_digit_nth_power, answers={4: 19316, 5: 443839})
