#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0074/p0074.py :: solve_digit_factorial_chains_p0074_s0.

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

Answer: 402
URL: https://projecteuler.net/problem=74"""
from __future__ import annotations

import sys


def show_solution() -> bool:
    return '--show' in sys.argv


digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def find_max_length_chains_digit_factorial(max_num: int) -> tuple[int, int]:
    chain_length_cache: dict[int, int] = {}
    graph: dict[int, int] = {}
    max_chain_length: int = 0
    max_chain_length_count: int = 0
    for start in range(2, max_num + 1):
        seen: list[int] = []
        current: int = start
        while current not in seen and current not in chain_length_cache:
            seen.append(current)
            if current not in graph:
                graph[current] = sum_of_digit_factorials(current)
            current = graph[current]
        if current in chain_length_cache:
            length = len(seen) + chain_length_cache[current]
        else:
            length = len(seen)
        for i, num in enumerate(seen):
            chain_length_cache[num] = length - i
            graph[num] = seen[i + 1] if i + 1 < len(seen) else current
        if (chain_length := chain_length_cache[start]) > max_chain_length:
            max_chain_length = chain_length
            max_chain_length_count = 1
        elif chain_length == max_chain_length:
            max_chain_length_count += 1
    return (max_chain_length, max_chain_length_count)


def solve(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = find_max_length_chains_digit_factorial(max_num)
    if show_solution():
        print(f'max_num={max_num!r} max_chain_length={max_chain_length!r}'
              f' max_chain_length_count={max_chain_length_count!r}', file=sys.stderr)
    return max_chain_length_count


if __name__ == '__main__':
    print(solve(max_num=int(sys.argv[1])))
