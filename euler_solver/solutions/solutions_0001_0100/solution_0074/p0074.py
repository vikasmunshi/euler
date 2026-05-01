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

Answer: 402
URL: https://projecteuler.net/problem=74
"""
from __future__ import annotations

from ctypes import POINTER, byref, c_int
from sys import maxsize
from typing import Any, Callable

from euler_solver.framework import (ColorCodes, evaluate, import_c_lib, logger, register_solution, show_solution,
                                    use_c_function)

euler_problem: int = 74
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_num': 10}, 'answer': 1},
    {'category': 'dev', 'input': {'max_num': 100}, 'answer': 2},
    {'category': 'dev', 'input': {'max_num': 1000}, 'answer': 12},
    {'category': 'dev', 'input': {'max_num': 10000}, 'answer': 42},
    {'category': 'dev', 'input': {'max_num': 100000}, 'answer': 42},
    {'category': 'main', 'input': {'max_num': 1000000}, 'answer': 402},
    {'category': 'extra', 'input': {'max_num': 5000000}, 'answer': 3240},
    {'category': 'extra', 'input': {'max_num': 10000000}, 'answer': 4680},
]

# Precompute factorials of digits 0-9 for fast lookup
digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880,)


def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def c_wrapper() -> tuple[Callable, ...]:
    error_null_output_ptrs = 1
    error_memory_allocation_cache = 2
    error_memory_allocation_seen = 3
    error_memory_reallocation_seen = 4

    # Import the C functions
    c_lib = import_c_lib(euler_problem)

    c_func_1 = getattr(c_lib, 'find_max_length_chains_digit_factorial')
    c_func_1.argtypes = [c_int, POINTER(c_int), POINTER(c_int)]
    c_func_1.restype = c_int

    def find_max_length_chains_digit_factorial_c(max_num: int) -> tuple[int, int]:
        """
        Compute the longest and most frequent digit factorial chain for numbers up to max_num (memoization algorithm).
        """
        if not (0 < max_num < maxsize):
            raise ValueError(f'max_num must be between 0 and {maxsize}')
        max_num_c = c_int(max_num)
        chain_count = c_int()
        max_length = c_int()
        result = c_func_1(max_num_c, byref(chain_count), byref(max_length))
        if result != 0:
            error_messages = {
                error_null_output_ptrs: "Null output pointers provided",
                error_memory_allocation_cache: "Failed to allocate memory for cache",
                error_memory_allocation_seen: "Failed to allocate memory for seen array",
                error_memory_reallocation_seen: "Failed to reallocate memory for seen array"
            }
            error_message = error_messages.get(result, f"Unknown error code: {result}")
            raise RuntimeError(f'Error in C function: {error_message} (max_num={int(max_num_c.value)})')
        return chain_count.value, max_length.value

    c_func_2 = getattr(c_lib, 'count_chains_with_max_length_digit_factorial')
    c_func_2.argtypes = [c_int, POINTER(c_int), POINTER(c_int)]
    c_func_2.restype = c_int

    def count_chains_with_max_length_digit_factorial_c(max_num: int) -> tuple[int, int]:
        """
        Compute the longest and most frequent digit factorial chain for numbers up to max_num
        (chain-building algorithm).
        """
        if not (0 < max_num < maxsize):
            raise ValueError(f'max_num must be between 0 and {maxsize}')
        max_num_c = c_int(max_num)
        chain_count = c_int()
        max_length = c_int()
        result = c_func_2(max_num_c, byref(chain_count), byref(max_length))
        if result != 0:
            error_messages = {
                error_null_output_ptrs: "Null output pointers provided",
                error_memory_allocation_cache: "Failed to allocate memory for cache",
                error_memory_allocation_seen: "Failed to allocate memory for seen array",
                error_memory_reallocation_seen: "Failed to reallocate memory for seen array"
            }
            error_message = error_messages.get(result, f"Unknown error code: {result}")
            raise RuntimeError(f'Error in C function: {error_message} (max_num={int(max_num_c.value)})')
        return chain_count.value, max_length.value

    return find_max_length_chains_digit_factorial_c, count_chains_with_max_length_digit_factorial_c


@use_c_function(c_wrapper, 0)
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
            # Add precomputed chain length if `current` exists in `chain_length_cache`
            length = len(seen) + chain_length_cache[current]
        else:
            # Length is simply the non-repeating terms from `seen`
            length = len(seen)
        # Propagate chain lengths back to all numbers in `seen`
        for i, num in enumerate(seen):
            chain_length_cache[num] = length - i
            graph[num] = seen[i + 1] if i + 1 < len(seen) else current
        if (chain_length := chain_length_cache[start]) > max_chain_length:
            max_chain_length = chain_length
            max_chain_length_count = 1
        elif chain_length == max_chain_length:
            max_chain_length_count += 1
    return max_chain_length, max_chain_length_count


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_factorial_chains_p0074_s0(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = find_max_length_chains_digit_factorial(max_num)
    if show_solution():
        print(f'{max_num=} {max_chain_length=} {max_chain_length_count=}')
    return max_chain_length_count


Chains = dict[int, list[int]]


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
            chains[val] = (current_chain[i:] if i >= loop_start else current_chain[i:])
    return True


def get_chain(max_num: int) -> Chains:
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    return chains


def print_chains(chains: Chains) -> None:
    for start, chain in sorted(chains.items()):
        cycle: int = sum_of_digit_factorials(chain[-1])
        print(f'{ColorCodes.GREEN}{start}{ColorCodes.RESET} -> ',
              ' -> '.join(
                      f'{ColorCodes.BLUE}{num}{ColorCodes.RESET}' if num == cycle else f'{num}' for num in chain[1:]),
              f' -> {ColorCodes.BLUE}{cycle}{ColorCodes.RESET}')
    max_chain_length: int = 0
    nums: list[int] = []
    for chain in chains.values():
        if len(chain) > max_chain_length:
            max_chain_length = len(chain)
        nums.extend(chain)
    unique_nums: set[int] = set(nums)
    print(f'{len(chains)=} {len(nums)=} {len(unique_nums)=} {len(nums)/len(unique_nums)=:.2f} {max_chain_length=}')


@use_c_function(c_wrapper, 1)
def count_chains_with_max_length_digit_factorial(max_num: int) -> tuple[int, int]:
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    chain_lengths = [len(c) for c in chains.values()]
    max_chain_length = max(chain_lengths)
    max_chain_length_count = chain_lengths.count(max_chain_length)
    return max_chain_length, max_chain_length_count


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digit_factorial_chains_p0074_s1(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num)
    if show_solution():
        print(f'{max_num=} {max_chain_length=} {max_chain_length_count=}')
    return max_chain_length_count


@register_solution(euler_problem=euler_problem, max_test_case_index=5)
def solve_digit_factorial_chains_p0074_s2(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num=max_num)
    if show_solution():
        if max_num <= 1_000:
            chains: Chains = get_chain(max_num)
            print_chains(chains)
        print(f'{max_num=} {max_chain_length=} {max_chain_length_count=}')
    return max_chain_length_count


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
