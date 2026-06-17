#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 93: Arithmetic Expressions [Level 8]. """
from __future__ import annotations

import functools

from solver.runners import runner


@functools.lru_cache(maxsize=None)
def eval_all_operations(vals: tuple[int | float, ...]) -> set[int | float]:
    """All values reachable from a value pool by repeated pairwise combination; memoised on the pool."""
    if (len_v := len(vals)) == 1:
        return {vals[0]}
    s = set()
    for i in range(len_v - 1):
        for j in range(i + 1, len_v):
            a, b = (vals[i], vals[j])
            r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
            s |= eval_all_operations(r + (a + b,))
            s |= eval_all_operations(r + (abs(a - b),))
            s |= eval_all_operations(r + (a * b,))
            if b > 0:
                s |= eval_all_operations(r + (a / b,))
            if a > 0:
                s |= eval_all_operations(r + (b / a,))
    return s


@runner.main
def solve(*args: str) -> str:
    """Recursive pool reduction enumerates every parenthesisation/operator choice; pick the digit set
    a<b<c<d with the longest consecutive run 1..n; O(1) over the fixed 126 digit sets."""
    max_digits: str = ""
    max_length: int = 0
    max_results: set[int] = set()
    for a in range(1, 7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                for d in range(c + 1, 10):
                    results: set[int] = {int(x) for x in eval_all_operations((a, b, c, d)) if x.is_integer()}
                    length = 0
                    while length + 1 in results:
                        length += 1
                    if length > max_length:
                        max_length, max_digits, max_results = (length, f"{a}{b}{c}{d}", results)
    if runner.show:
        print(f"max_digits={max_digits!r} max_length={max_length!r} max_results={max_results!r}")
    return str(max_digits)


if __name__ == "__main__":
    raise SystemExit(solve())
