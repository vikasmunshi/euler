#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 74: Digit Factorial Chains.

Problem Statement:
    The number 145 is well known for the property that the sum of the factorial of its digits
    is equal to 145:
        1! + 4! + 5! = 1 + 24 + 120 = 145.

    Perhaps less well known is 169, in that it produces the longest chain of numbers that link
    back to 169; it turns out that there are only three such loops that exist:
        169 -> 363601 -> 1454 -> 169
        871 -> 45361 -> 871
        872 -> 45362 -> 872

    It is not difficult to prove that EVERY starting number will eventually get stuck in a loop.
    For example:
        69 -> 363600 -> 1454 -> 169 -> 363601 (-> 1454)
        78 -> 45360 -> 871 -> 45361 (-> 871)
        540 -> 145 (-> 145)

    Starting with 69 produces a chain of five non-repeating terms, but the longest non-repeating
    chain with a starting number below one million is sixty terms.

    How many chains, with a starting number below one million, contain exactly sixty non-repeating terms?

Solution Approach:
    Use memoization to store chain lengths for numbers to avoid recomputation.
    Precompute factorials of digits 0-9 for fast lookup.
    For each starting number below one million, generate the digit factorial sum chain until
    a loop or repetition is detected.
    Count chains with exactly 60 non-repeating terms.
    The solution involves efficient simulation and caching for performance (O(n) expected).
    Number theory and combinatorics help to identify repeated loops and avoid redundant calculations.

Answer: [60, 402]
URL: https://projecteuler.net/problem=74
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from math import factorial
from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution

euler_problem: int = 74
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_num': 10}},
    {'category': 'preliminary', 'input': {'max_num': 100}},
    {'category': 'preliminary', 'input': {'max_num': 1000}},
    {'category': 'preliminary', 'input': {'max_num': 10000}},
    {'category': 'preliminary', 'input': {'max_num': 100000}},
    {'category': 'main', 'input': {'max_num': 1000000}}
]

digit_factorials: dict[str, int] = {str(d): factorial(d) for d in range(0, 10)}


def sum_digit_factorial(n: int) -> int:
    return sum((digit_factorials[d] for d in str(n)))


@lru_cache(maxsize=None)
def chain_len(n: int) -> int:
    num, chain = (n, {n})
    while (num := sum_digit_factorial(num)) not in chain:
        chain.add(num)
    return len(chain)


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_digit_factorial_chains_p0074_s0(*, max_num: int) -> list:
    chain_lengths = [1 if n == (next_n := sum_digit_factorial(n)) else chain_len(next_n) + 1
                     for n in range(1, max_num + 1)]
    length_counts: Counter[int] = Counter(chain_lengths)
    if show_solution():
        print(f'Chain lengths for max_num={max_num!r}: {sorted(length_counts.items())}')
    return sorted(max(length_counts.items()))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
