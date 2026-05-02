#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0095/p0095.py
  func: solve_amicable_chains_p0095_s0
"""

from __future__ import annotations

from sys import argv
from typing import Dict, List


def show_solution() -> bool:
    return "--show" in argv


def longest_amicable_chain(max_num: int) -> tuple[int, int]:
    divisor_sum: List[int] = [0] * (max_num + 1)
    for i in range(1, max_num // 2 + 1):
        for j in range(i * 2, max_num + 1, i):
            divisor_sum[j] += i
    smallest_member, longest_length = (0, 0)
    seen: Dict[int, int] = {}
    for i in range(1, max_num + 1):
        if i not in seen:
            ch, c, path = ({i}, divisor_sum[i], [i])
            while i <= c <= max_num and c not in ch:
                ch.add(c)
                path.append(c)
                c = divisor_sum[c]
            if c == i:
                if (len_ch := len(ch)) > longest_length:
                    longest_length, smallest_member = (len_ch, i)
                for x in path:
                    seen[x] = len_ch
    return (longest_length, smallest_member)


def solve(*, max_num: int) -> int:
    longest_length, smallest_member = longest_amicable_chain(max_num)
    if show_solution():
        print(
            f"Smallest Member of longest chain of length longest_length={
                longest_length!r} is smallest_member={
                smallest_member!r}")
    return smallest_member


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
