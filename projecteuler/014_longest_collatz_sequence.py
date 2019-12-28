#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=14
The following iterative sequence is defined for the set of positive integers:

n → n/2 (n is even)
n → 3n + 1 (n is odd)

Using the rule above and starting with 13, we generate the following sequence:

13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1
It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms.
Although it has not been proved yet (Collatz Problem), it is thought that all starting numbers finish at 1.

Which starting number, under one million, produces the longest chain?

NOTE: Once the chain starts the terms are allowed to go above one million.
Answer: 837799
"""
from functools import lru_cache


@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    return 1 if number == 1 else 1 + collatz_sequence_length(number // 2 if number % 2 == 0 else (3 * number) + 1)


def longest_collatz_sequence_generator(max_number: int) -> int:
    return max([(x, collatz_sequence_length(x)) for x in range(1, max_number + 1)], key=lambda i: i[1])[0]


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(longest_collatz_sequence_generator, answers={1000000: 837799})
