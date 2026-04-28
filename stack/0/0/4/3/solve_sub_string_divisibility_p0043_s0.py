#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0043/p0043.py :: solve_sub_string_divisibility_p0043_s0.

Project Euler Problem 43: Sub-string Divisibility.

Problem Statement:
    The number, 1406357289, is a 0 to 9 pandigital number because it is made up of each
    of the digits 0 to 9 in some order, but it also has a rather interesting sub-string
    divisibility property.

    Let d_1 be the 1st digit, d_2 be the 2nd digit, and so on. In this way, we note
    the following:
        d_2d_3d_4=406 is divisible by 2
        d_3d_4d_5=063 is divisible by 3
        d_4d_5d_6=635 is divisible by 5
        d_5d_6d_7=357 is divisible by 7
        d_6d_7d_8=572 is divisible by 11
        d_7d_8d_9=728 is divisible by 13
        d_8d_9d_10=289 is divisible by 17

    Find the sum of all 0 to 9 pandigital numbers with this property.

Solution Approach:
    Use permutations to generate all 0 to 9 pandigital numbers, then check the
    sub-string divisibility conditions based on given primes.
    Pruning early on failures reduces search space.
    Efficient divisibility checks are straightforward.
    The complexity is bounded by factorial(10) but pruning is crucial for feasibility.

Answer: 16695334890
URL: https://projecteuler.net/problem=43"""
from __future__ import annotations

import sys
from typing import Generator


def show_solution() -> bool:
    return '--show' in sys.argv


def solve() -> int:
    valid_multiples_of_17 = ('017', '034', '051', '068', '085', '102', '136', '153', '170', '187', '204', '238', '289',
                             '306', '340', '357', '374', '391', '408', '425', '459', '476', '493', '510', '527', '561',
                             '578', '612', '629', '680', '697', '714', '731', '748', '765', '782', '816', '850', '867',
                             '901', '918', '935', '952', '986')

    def gen_special_numbers(current_number: str | None = None, divisor: int = 17) -> Generator[int, None, None]:
        next_divisor: int | None = {3: 2, 5: 3, 7: 5, 11: 7, 13: 11, 17: 13}.get(divisor, None)
        if current_number is None:
            for num_str in valid_multiples_of_17:
                yield from gen_special_numbers(current_number=num_str, divisor=next_divisor)  # type: ignore[arg-type]
        else:
            for next_digit in (d for d in '0123456789' if d not in current_number):
                next_num: str = next_digit + current_number
                if int(next_num[:3]) % divisor != 0:
                    continue
                if next_divisor is None:
                    yield int(next((d for d in '0123456789' if d not in next_num)) + next_num)
                else:
                    yield from gen_special_numbers(current_number=next_num, divisor=next_divisor)

    if show_solution():
        result: int = 0
        for num in gen_special_numbers():
            result += num
            print(num, file=sys.stderr)
        return result
    return sum((num for num in gen_special_numbers()))


if __name__ == '__main__':
    sys.setrecursionlimit(10 ** 6)
    print(solve())
