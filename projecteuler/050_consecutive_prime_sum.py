#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=50
The prime 41, can be written as the sum of six consecutive primes:

41 = 2 + 3 + 5 + 7 + 11 + 13
This is the longest sum of consecutive primes that adds to a prime below one-hundred.

The longest sum of consecutive primes below one-thousand that adds to a prime, contains 21 terms, and is equal to 953.

Which prime, below one-million, can be written as the sum of the most consecutive primes?
Answer: 997651
"""
from itertools import accumulate


def solution(max_limit: int) -> int:
    sieve = [True] * (max_limit // 2)
    for i in range(3, int(max_limit ** 0.5) + 1, 2):
        if sieve[i // 2]:
            sieve[i * i // 2::i] = [False] * ((max_limit - i * i - 1) // (2 * i) + 1)
    primes = [2] + [2 * i + 1 for i in range(1, max_limit // 2) if sieve[i]]
    prime_sums = [0] + list(accumulate(primes))
    primes = set(primes)

    number_of_primes_in_sum, prime = 0, 0
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            possible_prime = prime_sums[i] - prime_sums[j]
            if possible_prime > max_limit:
                break
            if possible_prime in primes:
                number_of_primes_in_sum = i - j
                prime = possible_prime

    return prime


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(solution,
                                    answers={100: 41, 1000: 953, 10 ** 5: 92951, 10 ** 6: 997651, 10 ** 7: 9951191})
