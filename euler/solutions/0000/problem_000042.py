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
from typing import cast

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
    """
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

    Solution Approach:
    Determines the number of triangle words in a given text file. A triangle word is a word whose
    numerical value corresponds to a triangle number. The function takes a text file URL, reads
    its contents, processes each word, and counts how many of them are triangle words.

    Parameters
    ----------
    file_url : str
        The URL of the text file containing comma-separated words.

    Returns
    -------
    int
        The count of triangle words in the provided text file.

    Raises
    ------
    ValueError
        If the file contents cannot be processed correctly.

    Notes
    -----
    A triangle number is a number that can be arranged in an equilateral triangle. It is calculated
    using the formula n(n + 1) / 2, where n is a positive integer.

    To check if any number is a triangle number,
    we use the mathematical property that a number is triangular if and only if 8n+1 is a perfect square.
    """
    return sum(is_triangle_number(word_to_num(word)) for word in get_text_file(file_url).split(','))


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
