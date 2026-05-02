#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0068/p0068.py
  func: solve_magic_5_gon_ring_p0068_s0
"""

from __future__ import annotations

from collections import namedtuple
from itertools import permutations
from sys import argv
from typing import List, Set, Tuple

Ring = namedtuple("Ring", ["outer", "inner"])


def show_solution() -> bool:
    return "--show" in argv


Line = namedtuple("Line", ["outer", "inner_1", "inner_2"])


def solve(*, result_length: int, ring_size: int) -> int:
    n: int = ring_size
    index_range_n: Tuple[int, ...] = tuple(range(1, n))
    max_magic_number: int = 0
    max_ring, max_lines = (None, None)
    inner_loop_count: int = 0
    outer_loop_count: int = 0
    for inner_choice in permutations(range(1, min(9, 2 * n) + 1), n):
        outer_loop_count += 1
        inner_sums: Tuple[int, ...] = tuple((inner_choice[i] + inner_choice[(i + 1) % n] for i in range(n)))
        if len(set(inner_sums)) != n:
            continue
        outer_candidates: Set[int] = set((n for n in range(1, 2 * n + 1) if n not in inner_choice))
        outer_choice: List[int] = [min(outer_candidates)]
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
    if show_solution():
        print(f"Ring Size: {ring_size}; "
              f"Inner Loop Count: {inner_loop_count}; "
              f"Outer Loop Count: {outer_loop_count}; "
              f"Magic Number: {max_magic_number}; "
              f"Ring: {max_ring}; Lines: {max_lines}")
    assert result_length == len(str(max_magic_number)), "Result length does not match expected value"
    return max_magic_number


def main() -> int:
    print(solve(result_length=int(argv[1]), ring_size=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
