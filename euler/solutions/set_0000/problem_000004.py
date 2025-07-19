# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 4: Largest Palindrome Product

Problem Statement:
A palindromic number reads the same both ways. The largest palindrome made from the product
of two 2-digit numbers is 9009 = 91 × 99.

Find the largest palindrome made from the product of two 3-digit numbers.

Solution Approach:
This implementation uses an optimized algorithm to find palindrome products efficiently:

1. Start with the largest possible n-digit numbers for both factors to maximize chances of
   finding large palindromes early

2. Use the mathematical property that palindromes with an even number of digits are
   always divisible by 11, which means at least one of the factors must be divisible by 11

3. Implement early termination when the current product becomes smaller than the best
   palindrome found so far

4. Check palindromic property by converting to string and comparing with its reverse

5. Avoid duplicate checks by ensuring the second factor is never larger than the first

The optimizations significantly reduce the search space from O(10^(2n)) to approximately
O(10^(2n)/11) in the worst case, with typical performance being much better.

Test Cases:
- For size=2 (two-digit numbers): 9009 (91 × 99)
- For size=3 (three-digit numbers): 906609 (993 × 913)

URL: https://projecteuler.net/problem=4
Answer: 906609
"""

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=4)
problem_number: int = 4

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 2}, answer=9009, ),  # Largest palindrome product of two 2-digit numbers (91×99)
    ProblemArgs(kwargs={'n': 3}, answer=906609, ),  # Largest palindrome product of two 3-digit numbers (913*993)
    ProblemArgs(kwargs={'n': 4}, answer=99000099, ),  # Largest palindrome product of two 4-digit numbers (9901*9999)
    ProblemArgs(kwargs={'n': 5}, answer=9966006699, ),  # Largest palindrome product of 2 5-digit numbers (99681*99979)
]


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


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def largest_palindrome_product_of_two_n_digit_numbers(*, n: int) -> int:
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
        >>> largest_palindrome_product_of_two_n_digit_numbers(n=2)
        9009 # 91 × 99
        >>> largest_palindrome_product_of_two_n_digit_numbers(n=3)
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
    raise SystemExit(evaluate_solutions(problem_number))
