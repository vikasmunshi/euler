#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=40
An irrational decimal fraction is created by concatenating the positive integers:

0.123456789101112131415161718192021...

It can be seen that the 12th digit of the fractional part is 1.

If dn represents the nth digit of the fractional part, find the value of the following expression.

d1 × d10 × d100 × d1000 × d10000 × d100000 × d1000000
Answer: 210
"""
from functools import reduce


def solution(i: int) -> int:
    def get_nth_digit_champernowne_s_constant(n: int) -> int:
        length_till_num_digits, length_with_num_digits, num_digits = 0, 0, 0
        while length_with_num_digits < n:
            num_digits += 1
            length_till_num_digits = length_with_num_digits
            length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)

        offset_of_number = n - length_till_num_digits - 1
        digit_in_number = offset_of_number % num_digits
        number = 10 ** (num_digits - 1) + offset_of_number // num_digits
        return int(str(number)[digit_in_number])

    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    from .evaluate import Watchdog

    answers = {1: 1, 2: 5, 3: 15, 4: 105, 5: 210, 6: 210, 7: 1470, 8: 11760, 9: 11760, 10: 11760}
    with Watchdog() as wd:
        results = wd.evaluate_range(solution, answers=answers)
