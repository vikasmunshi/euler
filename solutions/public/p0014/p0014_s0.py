#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 14: Longest Collatz Sequence [Level 0]. """
from __future__ import annotations

import functools
from collections.abc import Callable

from solver.runners import runner


def plot_collatz_sequence_lengths_upto(number: int, length_of: Callable[[int], int]) -> None:
    """Plot the Collatz sequence lengths up to a given number."""
    import matplotlib.pyplot as plt

    numbers = range(1, number + 1)
    lengths = [length_of(i) for i in numbers]
    plt.title("Collatz Sequence Lengths")
    plt.plot(numbers, lengths)
    plt.xlabel("Number")
    plt.ylabel("Collatz Sequence Length")
    plt.tight_layout()
    plt.show()


@runner.main
def solve(*args: str) -> str:
    """Memoised recursion on Collatz chain length; ~O(N log N) for limit N.

    A fresh per-call cache (rebuilt every run, so each benchmarked run pays the
    full cost) records each chain length once, letting shared tails be reused.
    Only the upper half of the range is scanned: any x above the largest power of
    two below the limit dominates 2x in the lower half, whose chain is just x's
    with one extra step prepended.
    """
    max_number = runner.parse_int(args[0])

    @functools.lru_cache(maxsize=None)
    def collatz_length(number: int) -> int:
        """Number of terms in the Collatz chain from number down to 1."""
        if number == 1:
            return 1
        if number % 2 == 0:
            return 1 + collatz_length(number // 2)
        return 1 + collatz_length(3 * number + 1)

    max_length, starting_number = (0, 0)
    power_of_two: int = 2 ** (max_number.bit_length() - 1)
    for x in range(max_number, power_of_two, -1):
        length = collatz_length(x)
        if length > max_length:
            max_length, starting_number = (length, x)
    if runner.show:
        plot_collatz_sequence_lengths_upto(max_number, collatz_length)
    return str(starting_number)


if __name__ == "__main__":
    raise SystemExit(solve())
