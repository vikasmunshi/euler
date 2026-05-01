#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0022/p0022.py
  func: solve_names_scores_p0022_s0
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from sys import argv


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


@lru_cache(maxsize=None)
def word_to_num(word: str) -> int:
    return sum((ord(c) - 64 for c in word.strip('"') if c != " "))


def solve(*, file_url: str) -> int:
    return sum(
        (i * word_to_num(n) for i, n in enumerate(sorted((n for n in get_text_file(file_url).split(","))), start=1))
    )


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
