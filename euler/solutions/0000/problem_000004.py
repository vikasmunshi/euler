#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 4: Largest Palindrome Product

Problem Description:
A palindromic number reads the same both ways. The largest palindrome made from 
the product of two 2-digit numbers is 9009 = 91 × 99.
Find the largest palindrome made from the product of two n-digit numbers.

This solution uses multiple optimizations:
1. Starting with the largest possible factors to find large palindromes early
2. Using the mathematical property that for palindromes with even digits, at least
   one factor must be divisible by 11 (when the other is not)
3. Early termination when a path can't produce better results than already found

https://projecteuler.net/problem=4
"""
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases with known answers for verification
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'size': 2},
        answer=9009,  # Largest palindrome product of two 2-digit numbers (91×99)
    ),
    ProblemArgs(
        kwargs={'size': 3},
        answer=906609,  # Largest palindrome product of two 3-digit numbers (993×913)
    ),
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
    number = str(number)
    return number == ''.join(reversed(number))


def solution(*, size: int) -> int:
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
        size (int): The number of digits in each of the two factors
                   (e.g., 2 for two-digit numbers like 10-99)

    Returns:
        int: The largest palindromic number that is a product of two n-digit numbers

    Examples:
        >>> solution(size=2)
        9009 # 91 × 99
        >>> solution(size=3)
        906609 # 993 × 913
    """
    # Initialize with zero to handle edge cases (though shouldn't occur with valid inputs)
    largest_palindrome = 0
    # Calculate the upper and lower bounds for n-digit numbers
    max_number = 10 ** size - 1  # Largest n-digit number (e.g., 999 for size=3)
    min_number = 10 ** (size - 1)  # Smallest n-digit number (e.g., 100 for size=3)

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
            n = a * b

            # Early termination: if the current product is smaller than our best palindrome,
            # then all subsequent products with the current 'a' will also be smaller
            if n <= largest_palindrome:
                break

            # Check if the product is palindromic
            if is_palindromic(number=n):
                largest_palindrome = n

    return largest_palindrome


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
Solution to Project Euler Problem 4: Largest Palindrome Product

Problem Description:
A palindromic number reads the same both ways. The largest palindrome made from the product of two 2-digit numbers is 9009 = 91 × 99.
Find the largest palindrome made from the product of two n-digit numbers where n is the input parameter 'size'.

Approach:
1. Define the range of n-digit numbers (10^(n-1) to 10^n - 1)
2. Use a nested loop to check products of pairs of n-digit numbers
3. Use optimizations:
   - Start from the largest numbers to find large palindromes early
   - Use the property that for a palindrome product with even digits, at least one factor must be divisible by 11
     (This is because all palindromes with an even number of digits are divisible by 11)
   - Stop early when we can't exceed our current largest palindrome

Mathematical Insight:
For a 6-digit palindrome abccba, its decimal representation is:
100000a + 10000b + 1000c + 100c + 10b + a = 100001a + 10010b + 1100c = 11(9091a + 910b + 100c)

This proves that any palindrome with an even number of digits is divisible by 11,
which leads to our optimization that at least one of the factors must be divisible by 11.

Parameters:
    size (int): The number of digits in each factor

Returns:
    int: The largest palindromic product of two n-digit numbers

Examples:
    For size=2: Returns 9009 (product of 91 and 99)
    For size=3: Returns 906609 (product of 993 and 913)
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
