#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 99:

Problem Statement:
Comparing two numbers written in index form like 2^11 and 3⁷ is not difficult, as any calculator would confirm that
2^11 = 2048 < 3⁷ = 2187.

However, confirming that 632382^518061 > 519432^525806 would be much more difficult,
as both numbers contain over three million digits.

Using baseₑxp.txt (right click and 'Save Link/Target As...'), a 22K text file containing one thousand lines with a
base/exponent pair on each line, determine which line number has the greatest numerical value.

NOTE: The first two lines in the file represent the numbers in the example given above.

Solution Approach:
To compare numbers in exponential form like base^exponent without computing the actual values
(which can be extremely large), we can use logarithms. Since log(base^exponent) = exponent * log(base),
we can compare the logarithmic values instead of the actual numbers. The line with the highest
value of exponent * log(base) will contain the largest number.

Steps:
1. Read the base/exponent pairs from the file
2. For each pair, compute exponent * log(base)
3. Track the line number with the maximum value
4. Return the line number with the greatest value

Test Cases:

URL: https://projecteuler.net/problem=99
Answer: 709
"""
from math import log
from typing import List, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=99)
problem_number: int = 99

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0099_base_exp.txt'}, answer=709, ),
]


# Register this function as a solution for problem #99 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def largest_exponential(*, file_url: str) -> int:
    """
    Determine which line in a file has the base/exponent pair with the greatest numerical value.

    Uses logarithmic properties to compare exponential values without calculating the actual numbers,
    which could be extremely large with millions of digits.

    Args:
        file_url: URL to a text file containing base/exponent pairs (one per line, comma-separated)

    Returns:
        int: The line number (1-indexed) containing the base/exponent pair with the greatest value

    Raises:
        ValueError: If the file cannot be parsed or has invalid format
        RuntimeError: If no valid base/exponent pairs are found
    """
    try:
        # Retrieve the file content
        file_content = get_text_file(file_url)

        # Parse the file content into a list of (base, exponent) tuples
        numbers: List[Tuple[int, int]] = []
        for line in file_content.splitlines(keepends=False):
            try:
                parts = line.split(',')
                if len(parts) != 2:
                    continue  # Skip malformed lines
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
    # Initialize variables to track the maximum value and its position
    max_i, max_val, max_base, max_exp = 0, 0.0, 0, 0

    # Compare exponential values using logarithms: log(base^exponent) = exponent * log(base)
    # This allows comparison without computing the actual large numbers
    for i, (base, exponent) in enumerate(numbers, start=1):
        # Skip invalid inputs (non-positive values)
        if base <= 0 or exponent <= 0:
            print(f"Warning: Skipping invalid values at line {i}: base={base}, exponent={exponent}")
            continue

        # Calculate logarithmic value for comparison
        # Using natural logarithm for better numeric stability
        log_val = exponent * log(base)

        # Update maximum if current value is larger
        if log_val > max_val:
            max_i, max_val, max_base, max_exp = i, log_val, base, exponent
    if show_solution():
        print(f'Line {max_i} has the greatest exponential value (in log form: {max_val:.2f})')
        print(f'The actual number is {max_base}^{max_exp} which has approximately {int(max_val/log(10))+1} digits')
    return max_i


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
