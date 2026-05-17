#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 99: Largest Exponential [Level 2]. """
from __future__ import annotations

import math
import sys
from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources/" + src.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str) -> int:
    try:
        file_content = get_text_file(file_url)
        numbers: list[tuple[int, int]] = []
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
        log_val = exponent * math.log(base)
        if log_val > max_val:
            max_i, max_val, max_base, max_exp = (i, log_val, base, exponent)
    if sys.argv[-1] == "--show":
        print(f"Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})")
        print(f"The actual number is {max_base}^{max_exp} "
              f"which has approximately {int(max_val / math.log(10)) + 1} digits")
    return max_i


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
    raise SystemExit(main(file_url=str(argv[1])))
