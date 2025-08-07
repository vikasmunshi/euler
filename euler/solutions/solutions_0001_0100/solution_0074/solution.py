#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 74: Digit Factorial Chains.

  Problem Statement:
    The number 145 is well known for the property that the sum of the factorial of its
    digits is equal to 145: 1! + 4! + 5! = 1 + 24 + 120 = 145.

    Perhaps less well known is 169, in that it produces the longest chain of numbers
    that link back to 169; it turns out that there are only three such loops that
    exist:

    169 -> 363601 -> 1454 -> 169
    871 -> 45361 -> 871
    872 -> 45362 -> 872

    It is not difficult to prove that EVERY starting number will eventually get stuck
    in a loop. For example,

    69 -> 363600 -> 1454 -> 169 -> 363601 (-> 1454)
    78 -> 45360 -> 871 -> 45361 (-> 871)
    540 -> 145 (-> 145)

    Starting with 69 produces a chain of five non-repeating terms, but the longest
    non-repeating chain with a starting number below one million is sixty terms.

    How many chains, with a starting number below one million, contain exactly sixty
    non-repeating terms?

  Solution Approach:
    To solve this problem, consider the process of repeatedly replacing a number with
    the sum of the factorials of its digits. Investigate the chains formed by this
    process and focus on detecting loops and non-repeating terms within these chains.
    Efficiently compute factorial sums for digits 0-9 to reduce repetitive calculations.

    Use memoization or caching techniques to store the lengths of chains for numbers
    already computed to avoid redundant work. Start iterating from numbers below one
    million and follow their chains until a loop or previously known chain length is
    encountered.

    Count how many starting numbers produce a chain of exactly sixty non-repeating
    terms. Be mindful of the computational complexity and seek optimizations such as
    pruning chains once loops are detected or using bounds to limit unnecessary
    calculations.

  Test Cases:
    preliminary:
      max_num=10,
      answer=[1, 36].

      max_num=100,
      answer=[2, 54].

      max_num=1000,
      answer=[12, 55].

      max_num=10000,
      answer=[42, 60].

      max_num=100000,
      answer=[42, 60].

    main:
      max_num=1000000,
      answer=[60, 402].


  Answer: [60, 402]
  URL: https://projecteuler.net/problem=74
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from math import factorial

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution

digit_factorials: dict[str, int] = {str(d): factorial(d) for d in range(0, 10)}


def sum_digit_factorial(n: int) -> int:
    return sum((digit_factorials[d] for d in str(n)))


@lru_cache(maxsize=None)
def chain_len(n: int) -> int:
    num, chain = (n, {n})
    while (num := sum_digit_factorial(num)) not in chain:
        chain.add(num)
    return len(chain)


@register_solution(euler_problem=74, test_case_category=TestCaseCategory.EXTENDED)
def digit_factorial_chains(*, max_num: int) -> list:
    chain_lengths = [1 if n == (next_n := sum_digit_factorial(n)) else chain_len(next_n) + 1 for n in
                     range(1, max_num + 1)]
    length_counts: Counter[int] = Counter(chain_lengths)
    if show_solution():
        print(f'Chain lengths for max_num={max_num!r}: {sorted(length_counts.items())}')
    return sorted(max(length_counts.items()))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=74, time_out_in_seconds=300, mode='evaluate'))
