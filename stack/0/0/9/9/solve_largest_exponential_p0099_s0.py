#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0099/p0099.py
  func: solve_largest_exponential_p0099_s0
"""

from __future__ import annotations

from math import log
from pathlib import Path
from sys import argv
from typing import List, Tuple


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def show_solution() -> bool:
    return "--show" in argv


def solve(*, file_url: str) -> int:
    try:
        file_content = get_text_file(file_url)
        numbers: List[Tuple[int, int]] = []
        for line in file_content.splitlines(keepends=False):
            try:
                parts = line.split(",")
                if len(parts) != 2:
                    continue
                base = int(parts[0])
                exponent = int(parts[1])
                numbers.append((base, exponent))
            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse line: '{line}'. Error: {e}")
                continue
        if not numbers:
            raise RuntimeError("No valid base/exponent pairs found in the file")
    except Exception as e:
        raise ValueError(f"Error processing file: {e}")
    max_i, max_val, max_base, max_exp = (0, 0.0, 0, 0)
    for i, (base, exponent) in enumerate(numbers, start=1):
        if base <= 0 or exponent <= 0:
            print(f"Warning: Skipping invalid values at line {i}: base={base}, exponent={exponent}")
            continue
        log_val = exponent * log(base)
        if log_val > max_val:
            max_i, max_val, max_base, max_exp = (i, log_val, base, exponent)
    if show_solution():
        print(f"Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})")
        print(f"The actual number is {max_base}^{max_exp} which has approximately {int(max_val / log(10)) + 1} digits")
    return max_i


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
