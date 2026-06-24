#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 99: Largest Exponential [Level 2]. """
from __future__ import annotations

import math

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Rank each base^exp by the monotone surrogate exp*log(base) and take the argmax; O(N) over lines."""
    file_url = args[0]

    try:
        file_content = runner.get_text_file(file_url)
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
    # Single pass tracking the best log value and the 1-based line that produced it (argmax pattern).
    max_i, max_val, max_base, max_exp = (0, 0.0, 0, 0)
    for i, (base, exponent) in enumerate(numbers, start=1):
        if base <= 0 or exponent <= 0:
            print(f"Warning: Skipping invalid values at line {i}: base={base}, exponent={exponent}")
            continue
        # log(base^exponent) = exponent * log(base): order-preserving and computable in O(1).
        log_val = exponent * math.log(base)
        if log_val > max_val:
            max_i, max_val, max_base, max_exp = (i, log_val, base, exponent)
    if runner.show:
        print(f"Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})")
        print(f"The actual number is {max_base}^{max_exp} "
              f"which has approximately {int(max_val / math.log(10)) + 1} digits")
    return str(max_i)


if __name__ == "__main__":
    raise SystemExit(solve())
