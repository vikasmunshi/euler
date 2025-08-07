#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 99: Largest Exponential.

  Problem Statement:
    Comparing two numbers written in index form like 2 x 11 and 3 x 7 is not
    difficult, as any calculator would confirm that 2 x 11 = 2048 < 3 x 7 =
    2187.

    However, confirming that 632382 x 518061 > 519432 x 525806 would be much
    more difficult, as both numbers contain over three million digits.

    Using base_exp.txt (right click and 'Save Link/Target As...'), a 22K text
    file containing one thousand lines with a base/exponent pair on each line,
    determine which line number has the greatest numerical value.

    Note: The first two lines in the file represent the numbers in the example
    given above.

  Solution Approach:
    To solve this problem efficiently, you should avoid calculating the full
    numbers, as they are extremely large. Instead, use logarithms to compare
    values: for each base-exponent pair, compute the product of the exponent and
    logarithm of the base. The pair with the largest result corresponds to the
    largest number.

    Read the base-exponent pairs from the provided file, compute the comparison
    value for each, and track the line number with the maximum value. This approach
    leverages numerical properties and enables handling of very large numbers
    without overflow or performance issues.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0099_base_exp.txt,
      answer=709.


  Answer: 709
  URL: https://projecteuler.net/problem=99
"""
from __future__ import annotations

from math import log
from typing import List, Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution
from euler.setup.cached_requests import get_text_file


@register_solution(euler_problem=99, test_case_category=TestCaseCategory.EXTENDED)
def largest_exponential(*, file_url: str) -> int:
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
        print(f'Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})')
        print(f'The actual number is {max_base}^{max_exp} which has approximately {int(max_val / log(10)) + 1} digits')
    return max_i


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=99, time_out_in_seconds=300, mode='evaluate'))
