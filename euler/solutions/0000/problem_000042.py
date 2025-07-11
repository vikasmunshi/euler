#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 42: Coded triangle numbers

Problem Statement:
The nth term of the sequence of triangle numbers is given by, tn = ½n(n+1); 
so the first ten triangle numbers are:
1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...

By converting each letter in a word to a number corresponding to its alphabetical position
and adding these values we form a word value. For example, the word value for SKY is 
19 + 11 + 25 = 55 = t10. If the word value is a triangle number then we shall call the 
word a triangle word.

Using words.txt, a 16K text file containing nearly two-thousand common English words,
how many are triangle words?

Solution Approach:
This solution processes each word in the provided file by:
1. Converting each letter to its alphabetical position (A=1, B=2, etc.)
2. Summing these values to get the word's numerical value
3. Checking if the sum is a triangle number using the formula: 8n+1 is a perfect square
4. Counting how many words have triangle number values

Triangle numbers follow the pattern tn = n(n+1)/2, so we can efficiently determine if
a number is triangular without generating the entire sequence.

Test Cases:
- The file words.txt contains 162 triangle words

URL: https://projecteuler.net/problem=42
Answer: 162
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import word_to_num, get_text_file

# List of test cases for this problem
# Each case provides input parameters and expected output
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        # URL to the file containing the list of words to process
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0042_words.txt'},
        # Expected answer: 162 triangle words in the file
        answer=162,
    ),
]


def is_triangle_number(n: int) -> bool:
    """
    Check if a number is a triangle number.

    This function determines if a given number is a triangle number using the mathematical
    property that a number n is triangular if and only if 8n+1 is a perfect square.
    A triangle number is a number that can be represented as a triangular array of points.

    Args:
        n: The number to check

    Returns:
        True if n is a triangle number, False otherwise

    Example:
        >>> is_triangle_number(10)
        True  # 10 is the 4th triangle number
        >>> is_triangle_number(11)
        False  # 11 is not a triangle number
    """
    return (8 * n + 1) ** 0.5 % 1 == 0


def solution(*, file_url: str) -> int:
    """
    Count how many words in a file have triangle number values.

    This function processes a file containing comma-separated words, calculates the
    numerical value of each word by summing the alphabetical positions of its letters,
    and counts how many of these values are triangle numbers.

    Args:
        file_url: The URL of the text file containing comma-separated words

    Returns:
        The count of triangle words in the provided text file

    Example:
        >>> solution(file_url="https://projecteuler.net/resources/documents/0042_words.txt")
        162  # There are 162 triangle words in the provided file
    """
    return sum(is_triangle_number(word_to_num(word)) for word in get_text_file(file_url).split(','))


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
