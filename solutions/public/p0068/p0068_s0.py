#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 68: Magic 5-gon Ring [Level 4]. """
from __future__ import annotations

import collections
import itertools

from solver.runners import runner

Ring = collections.namedtuple("Ring", ["outer", "inner"])
Line = collections.namedtuple("Line", ["outer", "inner_1", "inner_2"])


@runner.main
def solve(*args: str) -> str:
    """Enumerate only the n inner-ring positions and force every outer value from the line-sum
    constraint outer[i] = S - (inner[i] + inner[i+1]), pinning the smallest free value at outer[0]
    to fix rotation; cap inner values at 9 so 10 stays outside (16 digits). O(P(min(9, 2n), n) * n).
    """
    result_length = runner.parse_int(args[0])
    ring_size = runner.parse_int(args[1])

    n: int = ring_size
    index_range_n: tuple[int, ...] = tuple(range(1, n))
    max_magic_number: int = 0
    max_ring, max_lines = (None, None)
    inner_loop_count: int = 0
    outer_loop_count: int = 0
    for inner_choice in itertools.permutations(range(1, min(9, 2 * n) + 1), n):
        outer_loop_count += 1
        inner_sums: tuple[int, ...] = tuple((inner_choice[i] + inner_choice[(i + 1) % n] for i in range(n)))
        # Equal inner sums would force two lines onto the same outer node - reject the candidate.
        if len(set(inner_sums)) != n:
            continue
        outer_candidates: set[int] = set((n for n in range(1, 2 * n + 1) if n not in inner_choice))
        # Pin the smallest free value at outer[0] to canonicalise the clockwise start.
        outer_choice: list[int] = [min(outer_candidates)]
        outer_candidates.remove(outer_choice[0])
        line_sum: int = outer_choice[0] + inner_sums[0]
        for i in index_range_n:
            inner_loop_count += 1
            # Force the outer value; a missing candidate (KeyError) aborts this arrangement.
            try:
                outer_candidates.remove((required := (line_sum - inner_sums[i])))
            except KeyError:
                break
            else:
                outer_choice.append(required)
        else:
            # All outer values assigned: concatenate the lines and keep the largest number.
            lines = tuple(zip(outer_choice, inner_choice, inner_choice[1:] + inner_choice[:1]))
            magic_number: int = int("".join(("".join((str(num) for num in line)) for line in lines)))
            if max_magic_number < magic_number:
                max_magic_number = magic_number
                max_ring = Ring(outer=tuple(outer_choice), inner=tuple(inner_choice))
                max_lines = tuple((Line(*line) for line in lines))
    if runner.show:
        print(f"Ring Size: {ring_size}; "
              f"Inner Loop Count: {inner_loop_count}; "
              f"Outer Loop Count: {outer_loop_count}; "
              f"Magic Number: {max_magic_number}; "
              f"Ring: {max_ring}; "
              f"Lines: {max_lines}")
    assert result_length == len(str(max_magic_number)), "Result length does not match expected value"
    return str(max_magic_number)


if __name__ == "__main__":
    raise SystemExit(solve())
