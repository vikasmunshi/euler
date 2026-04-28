#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0099/p0099.py :: solve_largest_exponential_p0099_s0.

Project Euler Problem 99: Largest Exponential.

Problem Statement:
    Comparing two numbers written in index form like 2^11 and 3^7 is not
    difficult, as any calculator would confirm that 2^11 = 2048 < 3^7 = 2187.

    However, confirming that 632382^518061 > 519432^525806 would be much more
    difficult, as both numbers contain over three million digits.

    Using a 22K text file base_exp.txt containing one thousand lines with a
    base/exponent pair on each line, determine which line number has the
    greatest numerical value.

    NOTE: The first two lines in the file represent the numbers in the example
    given above.

Solution Approach:
    Use logarithmic comparison to avoid direct handling of large numbers. For
    each base/exponent pair, compute exponent * log(base). The line with the
    largest value corresponds to the largest number. This involves simple
    file parsing and floating point computation. Runs efficiently in O(n).

Answer: 709
URL: https://projecteuler.net/problem=99"""
from __future__ import annotations

import sys
from math import log
from pathlib import Path
from typing import List, Tuple


def show_solution() -> bool:
    return '--show' in sys.argv


def get_text_file(url: str) -> str:
    """ Return the contents of a file from the 'resources' directory. """
    local_filename: str = 'resources' + '/' + url.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str) -> int:
    try:
        file_content = get_text_file(file_url)
        numbers: List[Tuple[int, int]] = []
        for line in file_content.splitlines(keepends=False):
            try:
                parts = line.split(',')
                if len(parts) != 2:
                    continue
                base = int(parts[0])
                exponent = int(parts[1])
                numbers.append((base, exponent))
            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse line: '{line}'. Error: {e}")
                continue
        if not numbers:
            raise RuntimeError('No valid base/exponent pairs found in the file')
    except Exception as e:
        raise ValueError(f'Error processing file: {e}')
    max_i, max_val, max_base, max_exp = (0, 0.0, 0, 0)
    for i, (base, exponent) in enumerate(numbers, start=1):
        if base <= 0 or exponent <= 0:
            print(f'Warning: Skipping invalid values at line {i}: base={base}, exponent={exponent}')
            continue
        log_val = exponent * log(base)
        if log_val > max_val:
            max_i, max_val, max_base, max_exp = (i, log_val, base, exponent)
    if show_solution():
        print(f'Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})', file=sys.stderr)
        print(f'The actual number is {max_base}^{max_exp} which has approximately {int(max_val / log(10)) + 1} digits',
              file=sys.stderr)
    return max_i


if __name__ == '__main__':
    print(solve(file_url=str(sys.argv[1])))
