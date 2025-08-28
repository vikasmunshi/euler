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

from functools import lru_cache
from typing import Any, Generator

import matplotlib.pyplot as plt

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution

euler_problem: int = 14
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_number': 1000000}},
    {'category': 'extended', 'input': {'max_number': 10000000}}
]


@use_wrapped_c_function('p0014')
def collatz_cache_context() -> Generator[None, None, None]:
    """Context manager to ensure C cache is assigned before execution and cleared after execution."""
    pass


@use_wrapped_c_function('p0014')
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


@register_solution(euler_problem=euler_problem, max_test_case=None)
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
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
