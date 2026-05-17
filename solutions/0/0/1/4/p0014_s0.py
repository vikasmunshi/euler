#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 14: Longest Collatz Sequence [Level 0]. """
from __future__ import annotations

import functools
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


@functools.lru_cache(maxsize=None)
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
    import matplotlib.pyplot as plt

    numbers = range(1, number + 1)
    lengths = [collatz_sequence_length(i) for i in numbers]
    plt.title("Collatz Sequence Lengths")
    plt.plot(numbers, lengths)
    plt.xlabel("Number")
    plt.ylabel("Collatz Sequence Length")
    plt.tight_layout()
    plt.show()


def solve(*, max_number: int) -> int:
    max_length, starting_number = (0, 0)
    power_of_two: int = 2 ** (max_number.bit_length() - 1)
    for x in range(max_number, power_of_two, -1):
        length = collatz_sequence_length(x)
        if length > max_length:
            max_length, starting_number = (length, x)
    if sys.argv[-1] == "--show":
        plot_collatz_sequence_lengths_upto(number=max_number)
    return starting_number


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(max_number=int(argv[1])))
