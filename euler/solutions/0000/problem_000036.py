#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 36: Double-base Palindromes
# https://projecteuler.net/problem=36
# Answer: answers = {1: 25, 2: 157, 3: 1772, 4: 18,228, 6: 872,187, 9: 2,609,044,274}
# 
# PROBLEM DESCRIPTION:
# The decimal number, 585 = 1001001001_2 (binary), is palindromic in both bases.
# Find the sum of all numbers, less than one million, which are palindromic in base 10 and base 2.
# (Please note that the palindromic number, in either base, may not include leading zeros.)
#
# SOLUTION APPROACH:
# Rather than checking all numbers up to a limit, this solution directly generates decimal palindromes
# and tests whether they are also binary palindromes. The key insights are:
#
# 1. We can efficiently generate all decimal palindromes by:
#    - For single-digit numbers: Just using 1-9
#    - For even-length palindromes: Taking a number and appending its reverse (e.g., 12 → 1221)
#    - For odd-length palindromes: Taking a number, adding a middle digit, and appending the reverse
#      (e.g., 12 + 3 + 21 = 12,321)
#
# 2. We then filter these palindromes to find those that are also palindromic in binary by:
#    - Converting to binary representation (removing '0b' prefix)
#    - Checking if the binary string equals its reverse
#
# 3. Finally, we sum the qualifying numbers
#
# OPTIMIZATIONS:
# - Direct generation of palindromes avoids checking unnecessary numbers
# - The parameter max_digits controls the maximum number of decimal digits to consider
# - Single-pass filtering using a generator expression minimizes memory usage
# - Early termination when exceeding max_digits length
#
# MATHEMATICAL NOTES:
# - All single-digit numbers (1-9) are palindromic in both decimal and binary bases
# - Even-length palindromes in base 10 may be odd-length in base 2 and vice versa
# - The sum grows rapidly with the number of digits allowed, as shown in the test cases
#
# TIME COMPLEXITY: O(10^(max_digits/2) * max_digits) - we generate ~10^(max_digits/2) palindromes
# and perform O(max_digits) work for each binary conversion and comparison
#
# SPACE COMPLEXITY: O(max_digits) - storage for string representations of numbers
import textwrap
from typing import Generator

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for validating the double-base palindrome solution
#
# Each test case specifies a maximum number of decimal digits to consider and the
# expected sum of all double-base palindromes within that range.
#
# The progression shows how the sum grows with larger ranges:
# - max_digits=1: Only single-digit numbers (1-9) that are also binary palindromes
# - max_digits=6: Corresponds to the original problem (numbers < 1,000,000)
# - max_digits=9: Extended test case showing solution works for very large ranges
#
# The growth rate is super-linear but sub-exponential, with each additional digit
# approximately multiplying the sum by a factor of 10-20.
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_digits': 1},  # Single-digit numbers only (1-9)
        answer=25,                 # Sum: 1+3+5+7+9=25 (only odd numbers are binary palindromes)
    ),
    ProblemArgs(
        kwargs={'max_digits': 2},  # Up to 2 digits (1-99)
        answer=157,                # Includes numbers like 33, 99 that are palindromic in both bases
    ),
    ProblemArgs(
        kwargs={'max_digits': 3},  # Up to 3 digits (1-999)
        answer=1772,               # Includes numbers like 313, 585, 717
    ),
    ProblemArgs(
        kwargs={'max_digits': 4},  # Up to 4 digits (1-9999)
        answer=18228,              # Includes numbers like 1001, 3663, 9009
    ),
    ProblemArgs(
        kwargs={'max_digits': 6},  # Up to 6 digits (original problem: < 1,000,000)
        answer=872187,             # Project Euler's expected answer
    ),
    ProblemArgs(
        kwargs={'max_digits': 9},  # Extended test (up to 999,999,999)
        answer=2609044274,         # Demonstrates solution works for larger ranges
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
    """Find the sum of numbers palindromic in both decimal and binary bases.

    This function solves Project Euler problem 36 by:
    1. Generating all decimal palindromes up to a maximum number of digits
    2. Filtering for those that are also palindromic in binary
    3. Computing the sum of these double-base palindromes

    A number is a double-base palindrome if it reads the same forwards and backwards
    in both decimal and binary representations. For example, 585 = 1001001001₂ is
    palindromic in both bases.

    Args:
        max_digits: The maximum number of decimal digits to consider

    Returns:
        The sum of all numbers with at most max_digits decimal digits that are
        palindromic in both decimal and binary bases

    Examples:
        solution(max_digits=1) -> 25 (sum of 1, 3, 5, 7, 9)
        solution(max_digits=2) -> 157
        solution(max_digits=6) -> 872,187 (solves the original problem for numbers < 1,000,000)

    Note:
        The original problem asks for numbers less than one million, which corresponds
        to max_digits=6. Other values are provided for testing and exploration.
    """
    return sum(number for number in generate_decimal_palindromes(max_digits)
               if number == int(str(bin(number))[2:][::-1], base=2))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 36: Double-base Palindromes
https://projecteuler.net/problem=36

Problem Description:
The decimal number, 585 = 1001001001₂ (binary), is palindromic in both bases.
Find the sum of all numbers, less than one million, which are palindromic in base 10 and base 2.
(Please note that the palindromic number, in either base, may not include leading zeros.)

Solution Approach:
1. Generate all decimal palindromes up to a specified number of digits
2. Check each one to determine if it's also a palindrome in binary
3. Sum the qualifying numbers

Algorithm Details:
- We generate decimal palindromes directly rather than checking all numbers
- For even-length palindromes: mirror the digits (e.g., 13 → 1331)
- For odd-length palindromes: insert a middle digit (e.g., 13 → 13531)
- Convert each palindrome to binary and check if it's still palindromic
- Use generator-based iteration to minimize memory usage

Performance Considerations:
- Direct generation of palindromes is much faster than checking all numbers
- The binary conversion and palindrome check are relatively efficient operations
- The solution scales well for the original problem (max_digits=6)

Example Cases:
- For max_digits=1: Sum = 25 (palindromes: 1, 3, 5, 7, 9)
- For max_digits=2: Sum = 157
- For max_digits=3: Sum = 1,772
- For max_digits=6: Sum = 872,187 (this solves the original problem)

Mathematical Insights:
- All single-digit numbers (except 0) are palindromic in both bases
- Numbers that are palindromic in decimal may not be in binary (and vice versa)
- The density of double-base palindromes decreases as numbers get larger
- Numbers with an even number of binary digits must have an even sum of binary digits
  to be palindromic in binary

Time Complexity: O(10^(max_digits/2) * max_digits)
Space Complexity: O(max_digits)

Interesting Observation:
The answer for max_digits=9 is over 2.6 billion, showing how quickly the sum grows
when extending the range of consideration beyond the original problem statement.
''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
