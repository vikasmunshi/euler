#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 68: Magic 5-gon Ring.

Problem Statement:
    Consider the following "magic" 3-gon ring, filled with the numbers 1 to 6, and each line
    adding to nine.

    Working clockwise, and starting from the group of three with the numerically lowest external
    node (4,3,2 in this example), each solution can be described uniquely. For example, the above
    solution can be described by the set: 4,3,2; 6,2,1; 5,1,3.

    It is possible to complete the ring with four different totals: 9, 10, 11, and 12. There are
    eight solutions in total.

    By concatenating each group it is possible to form 9-digit strings; the maximum string for a
    3-gon ring is 432621513.

    Using the numbers 1 to 10, and depending on arrangements, it is possible to form 16- and
    17-digit strings. What is the maximum 16-digit string for a "magic" 5-gon ring?

Solution Approach:
    Use combinatorial enumeration with backtracking to arrange numbers 1 to 10 in the 5-gon ring.
    Represent the ring as pairs of internal nodes and one external node per line summing equally.
    Generate all valid magic 5-gon rings, ensure the starting external node is the lowest for
    uniqueness, and form concatenated strings.
    Track the maximum 16-digit string lexicographically.
    Key techniques: combinatorics, backtracking, string manipulation. Expected to be solved
    efficiently with pruning.

Answer: 6531031914842725
URL: https://projecteuler.net/problem=68
"""
from __future__ import annotations

from collections import namedtuple
from itertools import permutations
from typing import Any, List, Set, Tuple

from euler_solver.framework import evaluate, logger, register_solution, show_solution

euler_problem: int = 68
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'result_length': 9, 'ring_size': 3},
     'answer': 432621513},
    {'category': 'dev', 'input': {'result_length': 12, 'ring_size': 4},
     'answer': 462723831516},
    {'category': 'main', 'input': {'result_length': 16, 'ring_size': 5},
     'answer': 6531031914842725},
    {'category': 'extra', 'input': {'result_length': 21, 'ring_size': 6},
     'answer': 692122310348451151719},
    {'category': 'extra', 'input': {'result_length': 26, 'ring_size': 7},
     'answer': 87494612611315115314321027},
    {'category': 'extra', 'input': {'result_length': 31, 'ring_size': 8},
     'answer': 5981381151614621624114712731039},
    {'category': 'extra', 'input': {'result_length': 36, 'ring_size': 9},
     'answer': 109518511716166215271473133812841149},
]

Line = namedtuple('Line', ['outer', 'inner_1', 'inner_2'])
Ring = namedtuple('Ring', ['outer', 'inner'])


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_magic_5_gon_ring_p0068_s0(*, result_length: int, ring_size: int) -> int:
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
            magic_number: int = int(''.join((''.join((str(num) for num in line)) for line in lines)))
            if max_magic_number < magic_number:
                max_magic_number = magic_number
                max_ring = Ring(outer=tuple(outer_choice), inner=tuple(inner_choice))
                max_lines = tuple((Line(*line) for line in lines))
    if show_solution():
        print(f'Ring Size: {ring_size}; Inner Loop Count: {inner_loop_count}; Outer Loop Count: {outer_loop_count}; '
              f'Magic Number: {max_magic_number}; Ring: {max_ring}; Lines: {max_lines}')
    assert result_length == len(str(max_magic_number)), 'Result length does not match expected value'
    return max_magic_number


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
