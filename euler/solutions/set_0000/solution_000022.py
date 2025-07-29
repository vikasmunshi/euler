#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 22: names_scores

Problem Statement:
  Using names.txt (right click and 'Save Link/Target As...'), a 46K text file
  containing over five-thousand first names, begin by sorting it into alphabetical
  order. Then working out the alphabetical value for each name, multiply this
  value by its alphabetical position in the list to obtain a name score. For
  example, when the list is sorted into alphabetical order, COLIN, which is worth
  3 + 15 + 12 + 9 + 14 = 53, is the 938th name in the list. So, COLIN would obtain
  a score of 938 * 53 = 49714. What is the total of all the name scores in the
  file?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=22
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.misc.word_to_num import word_to_num
from euler.setup import TestCase
from euler.setup.cached_requests import get_text_file

test_cases: list[TestCase] = [
    TestCase(
        answer=871198282,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0022_names.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #22
@register_solution(problem_number=22, test_cases=test_cases)
def names_scores(*, file_url: str) -> int:
    """
    Calculate the total of all name scores in the given file.

    This function processes a file containing names, calculates a score for each name based on
    its alphabetical position and letter values, and returns the sum of all scores.

    Problem Context:
    In Project Euler problem 22, we're given a file with over 5,000 names. The task is to:
    1. Sort the names alphabetically
    2. Calculate each name's value (sum of letter positions: A=1, B=2, etc.)
    3. Multiply each name's value by its position in the sorted list
    4. Sum all these products to get the final answer

    Implementation Steps:
    1. File Retrieval: The `get_text_file()` utility function handles:
       - Fetching the file from the provided URL (with caching to avoid redundant network requests)
       - Error handling for network issues and response validation
       - Reading the file content as text

    2. Parsing and Preparation:
       - Split the text on commas to get individual name entries: `get_text_file(file_url).split(',')`
       - The generator expression `n for n in ...` prepares each name for processing
       - The quotation marks around each name are removed in the `word_to_num()` function

    3. Sorting:
       - Use Python's built-in `sorted()` function to arrange names alphabetically
       - This is essential as the position in the sorted list affects each name's score

    4. Score Calculation:
       - The `enumerate(..., start=1)` function generates (position, name) pairs with 1-based indexing
       - For each pair (i, n):
         * Calculate the alphabetical value of the name using `word_to_num(n)`
         * Multiply by its position i in the sorted list
       - The generator expression `i * word_to_num(n) for i, n in ...` computes each name's score

    5. Final Summation:
       - The `sum()` function efficiently aggregates all name scores without creating intermediate lists
       - This single-line approach combines all the above steps in a memory-efficient way

    Algorithm Analysis:
    - Time Complexity: O(n log n) where n is the number of names
      * Sorting dominates the complexity (Python's Timsort is O(n log n))
      * String operations for each name are O(m) where m is the average name length
      * Overall complexity remains O(n log n) since m << n

    - Space Complexity: O(n) for storing the sorted list of names
      * The generator expressions minimize memory usage by avoiding intermediate lists
      * The sorted() function requires O(n) additional space

    - Optimizations:
      * The `word_to_num()` function is cached with @lru_cache to avoid recalculating values for
        repeated names (while rare in this problem, it's a good practice)
      * Using generator expressions prevents loading the entire processed dataset into memory
      * The file caching mechanism in `get_text_file()` avoids redundant network requests

    Key Python Features Used:
    - Generator expressions for memory-efficient data processing
    - Functional programming style (map/filter operations via comprehensions)
    - Built-in sorting with custom comparison
    - Function memoization with lru_cache
    - Clean string processing

    Args:
        file_url: URL of the text file containing the names

    Returns:
        The sum of all name scores

    Example:
        >>> # Example with a small subset of names
        >>> # For names "MARY","PATRICIA","LINDA" in alphabetical order:
        >>> # LINDA (12+9+14+4+1=40) at position 1: 1*40 = 40
        >>> # MARY (13+1+18+25=57) at position 2: 2*57 = 114
        >>> # PATRICIA (16+1+20+18+9+3+9+1=77) at position 3: 3*77 = 231
        >>> # Total: 40 + 114 + 231 = 385
    """
    # One-line implementation that:
    # 1. Gets the file content and splits it into names
    # 2. Sorts the names alphabetically
    # 3. Enumerates with 1-based indexing for position
    # 4. Calculates each name's score (position * alphabetical value)
    # 5. Sums all scores for the final result
    return sum(i * word_to_num(n) for i, n in enumerate(sorted(n for n in get_text_file(file_url).split(',')), start=1))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(22))
