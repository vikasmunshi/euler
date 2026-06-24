#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 22: Names Scores [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def word_to_num(word: str) -> int:
    """Alphabetical word value: sum of letter positions (A=1 … Z=26)."""
    return sum(ord(c) - 64 for c in word.strip('"') if c != " ")


@runner.main
def solve(*args: str) -> str:
    """Sort the names, then sum each name's word value weighted by its 1-based rank; O(n log n)."""
    file_url = args[0]

    names = sorted(runner.get_text_file(file_url).split(","))
    return str(sum(i * word_to_num(n) for i, n in enumerate(names, start=1)))


if __name__ == "__main__":
    raise SystemExit(solve())
