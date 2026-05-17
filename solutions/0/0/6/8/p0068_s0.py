#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 68: Magic 5-gon Ring [Level 4]. """
from __future__ import annotations

import collections
import itertools
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any

Ring = collections.namedtuple("Ring", ["outer", "inner"])
Line = collections.namedtuple("Line", ["outer", "inner_1", "inner_2"])


def solve(*, result_length: int, ring_size: int) -> int:
    n: int = ring_size
    index_range_n: tuple[int, ...] = tuple(range(1, n))
    max_magic_number: int = 0
    max_ring, max_lines = (None, None)
    inner_loop_count: int = 0
    outer_loop_count: int = 0
    for inner_choice in itertools.permutations(range(1, min(9, 2 * n) + 1), n):
        outer_loop_count += 1
        inner_sums: tuple[int, ...] = tuple((inner_choice[i] + inner_choice[(i + 1) % n] for i in range(n)))
        if len(set(inner_sums)) != n:
            continue
        outer_candidates: set[int] = set((n for n in range(1, 2 * n + 1) if n not in inner_choice))
        outer_choice: list[int] = [min(outer_candidates)]
        outer_candidates.remove(outer_choice[0])
        line_sum: int = outer_choice[0] + inner_sums[0]
        for i in index_range_n:
            inner_loop_count += 1
            try:
                outer_candidates.remove((required := (line_sum - inner_sums[i])))
            except KeyError:
                break
            else:
                outer_choice.append(required)
        else:
            lines = tuple(zip(outer_choice, inner_choice, inner_choice[1:] + inner_choice[:1]))
            magic_number: int = int("".join(("".join((str(num) for num in line)) for line in lines)))
            if max_magic_number < magic_number:
                max_magic_number = magic_number
                max_ring = Ring(outer=tuple(outer_choice), inner=tuple(inner_choice))
                max_lines = tuple((Line(*line) for line in lines))
    if sys.argv[-1] == "--show":
        print(f"Ring Size: {ring_size}; "
              f"Inner Loop Count: {inner_loop_count}; "
              f"Outer Loop Count: {outer_loop_count}; "
              f"Magic Number: {max_magic_number}; "
              f"Ring: {max_ring}; "
              f"Lines: {max_lines}")
    assert result_length == len(str(max_magic_number)), "Result length does not match expected value"
    return max_magic_number


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
    raise SystemExit(main(result_length=int(argv[1]), ring_size=int(argv[2])))
