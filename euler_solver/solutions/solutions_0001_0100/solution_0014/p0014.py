#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 14: Longest Collatz Sequence.

Problem Statement:
    The following iterative sequence is defined for the set of positive integers:

        n → n/2  (n is even)
        n → 3n + 1  (n is odd)

    Using the rule above and starting with 13, we generate the following sequence:
    13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1.

    It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms.
    Although it has not been proved yet (Collatz Problem), it is thought that all starting
    numbers finish at 1.

    Which starting number, under one million, produces the longest chain?

    NOTE: Once the chain starts the terms are allowed to go above one million.

Solution Approach:
    Use iterative computation with memoization to compute chain lengths efficiently.
    For each number under one million, compute the Collatz sequence length and store in a
    cache to avoid recomputation. Track the number with the longest sequence.
    Time complexity roughly O(N) with memoization; space O(N).

Answer: 837799
URL: https://projecteuler.net/problem=14
"""
from __future__ import annotations

from contextlib import contextmanager
from ctypes import c_longlong
from functools import lru_cache
from sys import maxsize
from typing import Any, Callable, Generator

import matplotlib.pyplot as plt

from euler_solver.framework import evaluate, import_c_lib, logger, register_solution, show_solution, use_c_function

euler_problem: int = 14
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_number': 1000000}, 'answer': 837799},
    {'category': 'extra', 'input': {'max_number': 10000000}, 'answer': 8400511},
]


@lru_cache(maxsize=1)
def c_wrapper() -> tuple[Callable, ...]:
    _c_lib = import_c_lib(euler_problem)
    # Resolve the C function symbols and set ctypes signatures
    _c_collatz_len = _c_lib.collatz_sequence_length
    _c_collatz_len.argtypes = [c_longlong]
    _c_collatz_len.restype = c_longlong
    _c_ensure_cache = _c_lib.ensure_cache
    _c_ensure_cache.argtypes = []
    _c_ensure_cache.restype = None
    _c_free_cache = _c_lib.free_cache
    _c_free_cache.argtypes = []
    _c_free_cache.restype = None

    @contextmanager
    def collatz_cache_context_c() -> Generator[None, None, None]:
        """Context manager to ensure C cache is assigned before execution and cleared after execution."""
        try:
            _c_ensure_cache()
            yield
        finally:
            _c_free_cache()

    def collatz_sequence_length_c(number: int) -> int:
        """CTypes-backed Collatz sequence length with context-managed cache.

        Mirrors the Python implementation collatz_sequence_length.
        Accepts a positive integer and returns the count of terms ending at 1.
        """
        if not (0 < number < maxsize):
            raise ValueError(f'number must be between 0 and {maxsize}')
        n = c_longlong(number)
        result: c_longlong = _c_collatz_len(n)
        return int(result)

    return collatz_cache_context_c, collatz_sequence_length_c


@use_c_function(c_wrapper, 0)
@contextmanager
def collatz_cache_context() -> Generator[None, None, None]:
    try:
        yield
    finally:
        return


@use_c_function(c_wrapper, 1)
@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    """Calculate the Collatz sequence length recursively with memoization."""
    if number == 1:
        return 1
    elif number % 2 == 0:
        return 1 + collatz_sequence_length(number // 2)
    else:
        return 1 + collatz_sequence_length(3 * number + 1)


def plot_collatz_sequence_lengths_upto(number: int) -> None:
    """Plot the Collatz sequence lengths up to a given number."""
    numbers = range(1, number + 1)
    lengths = [collatz_sequence_length(i) for i in numbers]
    plt.title('Collatz Sequence Lengths')
    plt.plot(numbers, lengths)
    plt.xlabel('Number')
    plt.ylabel('Collatz Sequence Length')
    plt.tight_layout()
    plt.show()


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_longest_collatz_sequence_p0014_s0(*, max_number: int) -> int:
    max_length, starting_number = 0, 0
    power_of_two: int = 2 ** (max_number.bit_length() - 1)
    with collatz_cache_context():
        for x in range(max_number, power_of_two, -1):  # Start from max_number and decrease
            length = collatz_sequence_length(x)
            if length > max_length:
                max_length, starting_number = length, x
        if show_solution():
            plot_collatz_sequence_lengths_upto(number=max_number)
    return starting_number


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
