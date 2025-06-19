#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 42
# https://projecteuler.net/problem=42
# Answer: 162
# Notes: 
"""Solution to Project Euler problem 42: Coded triangle numbers.

This module provides a solution to the triangle words problem. It identifies
words whose alphabetical value (sum of letter positions) forms a triangle number.

The solution involves:
1. Defining a mathematical test for triangle numbers
2. Reading words from a file
3. Converting each word to its alphabetical value
4. Counting words whose values are triangle numbers

Triangle numbers are of the form t_n = n(n+1)/2, and this module uses an efficient
formula to check if a number is triangular without generating the sequence.
"""
import textwrap

import requests

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import word_to_number

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
    """Check if a number is a triangle number.

    A triangle number t_n can be calculated as t_n = n(n+1)/2 where n > 0.
    This function uses the mathematical property that a number is triangular
    if and only if 8n+1 is a perfect square.

    Args:
        n: The number to check

    Returns:
        True if n is a triangle number, False otherwise
    """
    return (8 * n + 1) ** 0.5 % 1 == 0


def solution(*, file_url: str) -> int:
    """Count the number of triangle words in the given file.

    This function downloads a file containing words, processes each word to determine
    if its alphabetical value is a triangle number, and returns the count of such words.

    Args:
        file_url: URL of the text file containing comma-separated words in quotes

    Returns:
        The number of triangle words in the file

    Raises:
        HTTPError: If the file download fails
    """
    response = requests.get(file_url)
    response.raise_for_status()  # Raise an error if the request failed
    content = response.text  # Extract the raw content of the file
    return len([word for word in content.split(',') if is_triangle_number(word_to_number(word.strip('"')))])


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 42: Coded Triangle Numbers
https://projecteuler.net/problem=42

Problem Description:
The nth term of the sequence of triangle numbers is given by, t_n = (1/2)*n*(n+1); so the first ten triangle numbers are:
1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...
By converting each letter in a word to a number corresponding to its alphabetical position and adding these values
we form a word value.
For example, the word value for SKY is 19 + 11 + 25 = 55 = t_{10}.
If the word value is a triangle number then we shall call the word a triangle word.
Using words.txt (right click and 'Save Link/Target As...'), a 16K text file containing
nearly two-thousand common English words, how many are triangle words?

Approach:
1. Mathematical foundation: A number n is triangular if and only if 8n+1 is a perfect square.
   This allows us to quickly test if a number is triangular without generating the sequence.

2. File processing: Download and parse the comma-separated words file, removing quotation marks.

3. Word conversion: For each word, calculate its alphabetical value by summing the position
   values of its letters (A=1, B=2, ..., Z=26). We use the word_to_number utility function.

4. Triangle test: For each word value, determine if it's a triangle number using our efficient test.

5. Count calculation: Count how many words have triangle number values.

Optimizations:
- The is_triangle_number function uses a mathematical property to avoid generating triangle numbers.
- We use a list comprehension for efficient filtering and counting in a single operation.
- The word_to_number function is decorated with @lru_cache to avoid recalculating values for
  repeated words.

Time Complexity: O(n*m) where n is the number of words and m is the average word length.
Space Complexity: O(n) for storing the filtered list during the list comprehension.
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
