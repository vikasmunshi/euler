#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=10
The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

Find the sum of all the primes below two million.
Answer: 142913828922
"""


def gen_primes_rolling_sieve(max_limit: int) -> {int}:
    def rolling_sieve():
        composites = dict()
        number = 2
        while number <= max_limit:
            if number in composites:
                for prime in composites[number]:
                    composites.setdefault(prime + number, []).append(prime)
                del composites[number]
            else:
                yield number  # number is prime
                composites[number * number] = [number]
            number += 1

    return tuple(rolling_sieve())


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
    return (2,) + tuple(2 * n + 1 for n in numbers if n != 0)


def sum_primes_rolling_sieve(max_num: int) -> int:
    return sum(gen_primes_rolling_sieve(max_num))


def sum_primes_sundaram_sieve(max_num: int) -> int:
    return sum(gen_primes_sundaram_sieve(max_num))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        wd.evaluate_compare((sum_primes_rolling_sieve, sum_primes_sundaram_sieve),
                            answers={10: 17, 2000000: 142913828922})
