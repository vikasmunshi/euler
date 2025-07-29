#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 4: largest_palindrome_product

Problem Statement:
  A palindromic number reads the same both ways. The largest palindrome made from
  the product of two 2-digit numbers is 9009 = 91 * 99. Find the largest
  palindrome made from the product of two 3-digit numbers.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=4
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase


def is_palindromic(*, number: int) -> bool:
    """
    Check if a number is palindromic (reads the same forwards and backwards).

    A palindromic number remains unchanged when its digits are reversed.
    For example, 9009 is palindromic because 9009 reversed is still 9009.

    Args:
        number (int): The integer to check for palindromic property

    Returns:
        bool: True if the number is palindromic, False otherwise

    Examples:
        >>> is_palindromic(number=9009)
        True
        >>> is_palindromic(number=1234)
        False
    """
    str_number: str = str(number)
    return str_number == ''.join(reversed(str_number))


test_cases: list[TestCase] = [
    TestCase(
        answer=9009,
        is_main_case=False,
        kwargs={'n': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=906609,
        is_main_case=False,
        kwargs={'n': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=99000099,
        is_main_case=False,
        kwargs={'n': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9966006699,
        is_main_case=False,
        kwargs={'n': 5},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #4
@register_solution(problem_number=4, test_cases=test_cases)
def largest_palindrome_product(*, n: int) -> int:
    """
    Find the largest palindrome made from the product of two n-digit numbers.

    This function uses an optimized algorithm that:
    1. Starts with the largest possible n-digit numbers for both factors
    2. Uses the mathematical property that for palindromes with even number
       of digits, if one factor is not divisible by 11, the other factor must be
    3. Breaks early from searches that cannot improve the current best result

    Complexity Analysis:
    - Time Complexity: O(10^(2n) / 11) worst case, but typically much better due to optimizations
    - Space Complexity: O(1) - uses only a constant amount of memory regardless of input size

    Args:
        n (int): The number of digits in each of the two factors (e.g., 2 for two-digit numbers like 10-99)

    Returns:
        int: The largest palindromic number that is a product of two n-digit numbers

    Examples:
        >>> largest_palindrome_product(n=2)
        9009 # 91 × 99
        >>> largest_palindrome_product(n=3)
        906609 # 993 × 913
    """
    # Initialize with zero to handle edge cases (though shouldn't occur with valid inputs)
    largest_palindrome: int = 0
    a_max: int = 0
    b_max: int = 0
    # Calculate the upper and lower bounds for n-digit numbers
    max_number: int = 10 ** n - 1  # Largest n-digit number (e.g., 999 for size=3)
    min_number: int = 10 ** (n - 1)  # Smallest n-digit number (e.g., 100 for size=3)

    # Find the largest multiple of 11 less than or equal to max_number
    # This optimization is based on the mathematical property that palindromes with
    # even number of digits are always divisible by 11. Therefore, at least one of
    # the factors must be divisible by 11 for their product to be a palindrome.
    max_multiple_11 = max_number - (max_number % 11)

    # Iterate through possible first factors in descending order (optimization)
    # Starting with larger numbers increases the chances of finding large palindromes early
    for a in range(max_number, min_number, -1):
        # Check if the current number is divisible by 11
        a_is_multiple_11 = a % 11 == 0

        # For the second factor b:
        # - If 'a' is divisible by 11, we can use any number from max_number down to 'a'
        # - If 'a' is not divisible by 11, we only need to check multiples of 11 (optimization)
        # We ensure 'b' ≤ 'a' to avoid duplicate checks (since a×b = b×a)
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            # Calculate the product
            ab = a * b

            # Early termination: if the current product is smaller than our best palindrome,
            # then all subsequent products with the current 'a' will also be smaller
            if ab <= largest_palindrome:
                break

            # Check if the product is palindromic
            if is_palindromic(number=ab):
                a_max, b_max, largest_palindrome = a, b, ab
    if show_solution():
        print(f'Largest palindrome that is a multiple of two {n}-digit numbers is '
              f'{largest_palindrome} ({a_max}x{b_max})')
    return largest_palindrome


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(4))
