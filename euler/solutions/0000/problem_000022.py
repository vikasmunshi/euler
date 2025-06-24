#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 22
# https://projecteuler.net/problem=22
# Answer: 871198282
# Notes:
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol
from euler.utils import word_to_num, get_text_file

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0022_names.txt'}, answer=871198282, ),
]


def solution(*, file_url: str) -> int:
    """
    solution to Project Euler problem 22
    https://projecteuler.net/problem=22
    Using names.txt (right click and 'Save Link/Target As...'), a 46K text file containing over five-thousand first names,
    begin by sorting it into alphabetical order. Then working out the alphabetical value for each name,
    multiply this value by its alphabetical position in the list to obtain a name score.
    For example, when the list is sorted into alphabetical order,
    COLIN, which is worth 3 + 15 + 12 + 9 + 14 = 53, is the 938th name in the list.
    So, COLIN would obtain a score of 938 * 53 = 49,714.
    What is the total of all the name scores in the file?

    Implementation Steps:
    1. Fetch the names list as a text file from the provided URL using the requests library.
       If the request fails, an exception is raised with raise_for_status().
    2. Parse the file content by:
       - Splitting the string on commas to extract individual names.
       - Removing the surrounding quotation marks from each name using strip.
       - The names in the file are already in uppercase, so no conversion is needed.
    3. Sort the names lexicographically (alphabetical order) using Python's built-in sorted() function.
    4. Compute the score for each name:
       - The alphabetical value of a name is calculated as the sum of the positions of its characters in the
         alphabet ('A' = 1, ..., 'Z' = 26). This is done using the word_to_number() utility function.
       - Multiply the alphabetical value by the name's position in the sorted list (1-based indexing).
    5. Sum the scores of all names to compute the final result using a generator expression with sum().
    6. Return the total score as the solution.

    Algorithm Analysis:
    - Time Complexity: O(n log n) due to the sorting operation, where n is the number of names.
    - Space Complexity: O(n) for storing the sorted list of names.
    - The solution uses a generator expression to compute the sum efficiently without creating intermediate lists.
    - The word_to_number function is cached with @lru_cache to improve performance for repeated calculations.

    This implementation demonstrates efficient parsing, sorting, and numerical computation using Python's
    built-in features and functional programming concepts.
    """
    return sum(i * word_to_num(n) for i, n in enumerate(sorted(n for n in get_text_file(file_url).split(',')), start=1))


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
