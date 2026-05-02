#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0014/p0014.py
  func: solve_longest_collatz_sequence_p0014_s0
"""

from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from sys import argv, setrecursionlimit
from typing import Generator

import matplotlib.pyplot as plt


def show_solution() -> bool:
    return "--show" in argv


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
    plt.title("Collatz Sequence Lengths")
    plt.plot(numbers, lengths)
    plt.xlabel("Number")
    plt.ylabel("Collatz Sequence Length")
    plt.tight_layout()
    plt.show()


@contextmanager
def collatz_cache_context() -> Generator[None, None, None]:
    try:
        yield
    finally:
        return


def solve(*, max_number: int) -> int:
    max_length, starting_number = (0, 0)
    power_of_two: int = 2 ** (max_number.bit_length() - 1)
    with collatz_cache_context():
        for x in range(max_number, power_of_two, -1):
            length = collatz_sequence_length(x)
            if length > max_length:
                max_length, starting_number = (length, x)
        if show_solution():
            plot_collatz_sequence_lengths_upto(number=max_number)
    return starting_number


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(max_number=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
