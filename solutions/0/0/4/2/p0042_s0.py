#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 42: Coded Triangle Numbers [Level 0]. """
from __future__ import annotations

import functools

from solver.runners import runner


def is_triangle_number(n: int) -> bool:
    """True iff n is triangular, tested via the inverse identity: 8n+1 is a perfect square."""
    result: bool = ((8 * n + 1) ** 0.5).is_integer()
    return result


@functools.lru_cache(maxsize=None)
def word_to_num(word: str) -> int:
    """Word value: sum of 1-based alphabet positions (A=1..Z=26) of each letter."""
    return sum((ord(c) - 64 for c in word.strip('"') if c != " "))


@runner.main
def solve(*args: str) -> str:
    """Count words whose value is triangular via the 8n+1-perfect-square test; O(W*L) over W words."""
    file_url = args[0]

    return str(sum((is_triangle_number(word_to_num(word)) for word in runner.get_text_file(file_url).split(","))))


if __name__ == "__main__":
    raise SystemExit(solve())
