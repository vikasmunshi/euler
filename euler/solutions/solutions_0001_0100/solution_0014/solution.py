#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 14: Longest Collatz Sequence.

  Problem Statement:
    The following iterative sequence is defined for the set of positive integers:

    n -> n / 2 (n is even)
    n -> 3 n + 1 (n is odd)

    Using the rule above and starting with 13, we generate the following sequence:
    13 -> 40 -> 20 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1.

    It can be seen that this sequence (starting at 13 and finishing at 1) contains
    10 terms. Although it has not been proved yet (Collatz Problem), it is thought
    that all starting numbers finish at 1.

    Which starting number, under one million, produces the longest chain?

    NOTE: Once the chain starts the terms are allowed to go above one million.

  Solution Approach:
    To solve this problem efficiently, implement memoization to store the sequence
    lengths for previously computed numbers, reducing redundant computations.
    Start from each number under one million and generate the Collatz sequence,
    recording the length until reaching 1. Maintain a record of the longest
    sequence and its starting number. This approach leverages dynamic
    programming concepts to optimize the exploration of the Collatz sequences.

  Test Cases:
    main:
      max_number=1000000,
      answer=837799.

    extended:
      max_number=10000000,
      answer=8400511.


  Answer: 837799
  URL: https://projecteuler.net/problem=14
"""
from __future__ import annotations

from functools import lru_cache

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    return 1 if number == 1 else 1 + collatz_sequence_length(number // 2 if number % 2 == 0 else 3 * number + 1)


@register_solution(euler_problem=14, test_case_category=TestCaseCategory.EXTENDED)
def longest_collatz_sequence(*, max_number: int) -> int:
    return max(((x, collatz_sequence_length(x)) for x in range(max_number, 4, -1)), key=lambda i: i[1])[0]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=14, time_out_in_seconds=300, mode='evaluate'))
