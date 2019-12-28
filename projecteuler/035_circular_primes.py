#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=35
The number, 197, is called a circular prime because all rotations of the digits: 197, 971, and 719 are themselves prime.

There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, and 97.

How many circular primes are there below one million?
Answer: 55
"""


def gen_primes_sundaram_sieve(max_limit: int) -> {int}:
    if max_limit < 2:
        return {2}
    max_number = (max_limit - 1) // 2 + 1
    numbers = list(range(0, max_number))
    for i in range(1, max_number):
        for j in range(i, max_number):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not a prime as 0
            except IndexError:
                break
    return {2 * n + 1 for n in numbers if n != 0}.union({2})


def get_rotated_numbers(num: int) -> [int]:
    return [
        int(str_num[-rot:] + str_num[:-rot])
        for str_num in (str(num),)
        for rot in range(1, len(str_num) + 1)
    ]


def num_circular_primes(max_limit: int) -> int:
    primes = gen_primes_sundaram_sieve(max_limit)
    circular_primes = [
        prime for prime in primes
        if not any(rotated_number not in primes for rotated_number in get_rotated_numbers(prime))
    ]
    return len(circular_primes)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(func=num_circular_primes, answers={10: 4, 100: 13, 10 ** 6: 55})
