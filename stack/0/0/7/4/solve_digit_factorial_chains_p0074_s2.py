#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0074/p0074.py :: solve_digit_factorial_chains_p0074_s2.

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

from enum import StrEnum


def show_solution() -> bool:
    return '--show' in sys.argv


class ColorCodes(StrEnum):
    GREEN = '\x1b[92m'
    YELLOW = '\x1b[93m'
    RED = '\x1b[91m'
    ORANGE = '\x1b[38;5;208m'
    BLUE = '\x1b[94m'
    CYAN = '\x1b[96m'
    MAGENTA = '\x1b[95m'
    WHITE = '\x1b[97m'
    BLACK = '\x1b[30m'
    GRAY = '\x1b[90m'
    BOLD = '\x1b[1m'
    UNDERLINE = '\x1b[4m'
    RESET = '\x1b[0m'


digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


Chains = dict[int, list[int]]


def print_chains(chains: Chains) -> None:
    for start, chain in sorted(chains.items()):
        cycle: int = sum_of_digit_factorials(chain[-1])
        print(f'{ColorCodes.GREEN}{start}{ColorCodes.RESET} -> ',
              ' -> '.join((f'{ColorCodes.BLUE}{num}{ColorCodes.RESET}' if num == cycle else f'{num}'
                           for num in chain[1:])),
              f' -> {ColorCodes.BLUE}{cycle}{ColorCodes.RESET}',
              file=sys.stderr)
    max_chain_length: int = 0
    nums: list[int] = []
    for chain in chains.values():
        if len(chain) > max_chain_length:
            max_chain_length = len(chain)
        nums.extend(chain)
    unique_nums: set[int] = set(nums)
    print(f'len(chains)={len(chains)!r} len(nums)={len(nums)!r} len(unique_nums)={len(unique_nums)!r} '
          f'len(nums)/len(unique_nums)={len(nums) / len(unique_nums):.2f} max_chain_length={max_chain_length!r}',
          file=sys.stderr)


def add_chains(chains: Chains, number: int) -> bool:
    if number in chains:
        return False
    num: int = number
    current_chain: list[int] = []
    visited: set[int] = set()
    while num not in visited:
        visited.add(num)
        if num in chains:
            current_chain.extend(chains[num])
            break
        current_chain.append(num)
        num = sum_of_digit_factorials(num)
    loop_start: int = len(current_chain) - len(visited) if num in visited else -1
    for i, val in enumerate(current_chain):
        if val not in chains:
            chains[val] = current_chain[i:] if i >= loop_start else current_chain[i:]
    return True


def get_chain(max_num: int) -> Chains:
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    return chains


def count_chains_with_max_length_digit_factorial(max_num: int) -> tuple[int, int]:
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    chain_lengths = [len(c) for c in chains.values()]
    max_chain_length = max(chain_lengths)
    max_chain_length_count = chain_lengths.count(max_chain_length)
    return (max_chain_length, max_chain_length_count)


def solve(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num=max_num)
    if show_solution():
        if max_num <= 1000:
            chains: Chains = get_chain(max_num)
            print_chains(chains)
        print(f'max_num={max_num!r} max_chain_length={max_chain_length!r} '
              f'max_chain_length_count={max_chain_length_count!r}', file=sys.stderr)
    return max_chain_length_count


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))
