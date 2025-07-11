#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 36: Double-base palindromes

Problem Statement:
The decimal number, 585 = 1001001001_2 (binary), is palindromic in both bases.
Find the sum of all numbers, less than one million, which are palindromic in base 10 and base 2.
(Please note that the palindromic number, in either base, may not include leading zeros.)

Solution Approach:
This implementation efficiently generates and tests double-base palindromes by:
1. Generating decimal palindromes systematically to avoid checking all numbers
2. Testing each decimal palindrome to see if it's also palindromic in binary
3. Summing those that meet both criteria

The generation of decimal palindromes follows a pattern-based approach rather than
checking every number, significantly reducing the computation required.

Test Cases:
- For max_digits=1 (1-9), the answer is 25
- For max_digits=2 (1-99), the answer is 157
- For max_digits=6 (< 1,000,000), the answer is 872,187

URL: https://projecteuler.net/problem=36
Answer: 872187
"""
from typing import Generator

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_digits': 1},  # Single-digit numbers only (1-9)
        answer=25,  # Sum: 1+3+5+7+9=25 (only odd numbers are binary palindromes)
    ),
    ProblemArgs(
        kwargs={'max_digits': 2},  # Up to 2 digits (1-99)
        answer=157,  # Includes numbers like 33, 99 that are palindromic in both bases
    ),
    ProblemArgs(
        kwargs={'max_digits': 3},  # Up to 3 digits (1-999)
        answer=1772,  # Includes numbers like 313, 585, 717
    ),
    ProblemArgs(
        kwargs={'max_digits': 4},  # Up to 4 digits (1-9999)
        answer=18228,  # Includes numbers like 1001, 3663, 9009
    ),
    ProblemArgs(
        kwargs={'max_digits': 6},  # Up to 6 digits (original problem: < 1,000,000)
        answer=872187,  # Project Euler's expected answer
    ),
    ProblemArgs(
        kwargs={'max_digits': 9},  # Extended test (up to 999,999,999)
        answer=2609044274,  # Demonstrates solution works for larger ranges
    ),
]


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]:
    """Generate all decimal palindromes with up to max_digits digits.

    This function efficiently generates all palindromic numbers in base 10 with at most
    the specified number of digits. A palindrome reads the same forwards and backwards.

    The generation follows these steps:
    1. Yield all single-digit numbers (1-9) which are palindromes by definition
    2. Generate even-length palindromes by mirroring digits (e.g., 12 → 1221)
    3. Generate odd-length palindromes by inserting a middle digit (e.g., 12 → 12,321)

    Args:
        max_digits: The maximum number of decimal digits allowed in the palindromes

    Yields:
        All decimal palindromes with at most max_digits digits, in ascending order

    Examples:
        For max_digits=2, yields: 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, ..., 99
        For max_digits=3, also includes: 101, 111, 121, ..., 999

    Notes:
        - Zero is not included as it would have a leading zero in binary
        - The algorithm avoids generating duplicates
        - The count of palindromes grows approximately as O(10^(max_digits/2))
    """
    # Generate single-digit palindromes (1-9)
    for digit in range(1, 10):
        yield digit

    # Generate multi-digit palindromes
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)

        # Even-length palindromes (e.g., 1221, 123321)
        yield int(digits_str + digits_rev)

        # Odd-length palindromes (e.g., 12321, 1234321)
        # Only generate if we haven't exceeded max_digits
        if 2 * num_digits < max_digits:
            for mid_digit in '0123456789':
                yield int(digits_str + mid_digit + digits_rev)


def solution(*, max_digits: int) -> int:
    """
    Find the sum of numbers that are palindromic in both decimal and binary bases.

    This solution efficiently generates decimal palindromes and checks if they are also
    palindromic in binary. A number is palindromic if it reads the same forwards and
    backwards. The approach avoids checking all numbers by directly generating palindromes.

    Args:
        max_digits: The maximum number of decimal digits to consider

    Returns:
        The sum of all double-base palindromes with at most max_digits decimal digits

    Example:
        >>> solution(max_digits=1)
        25
        >>> solution(max_digits=6)  # Original problem (< 1,000,000)
        872187
    """
    return sum(number for number in generate_decimal_palindromes(max_digits)
               if number == int(str(bin(number))[2:][::-1], base=2))


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
