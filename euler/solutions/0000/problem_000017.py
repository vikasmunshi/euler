# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 17: Number Letter Counts

Problem Statement:
If the numbers 1 to 5 are written out in words: one, two, three, four, five, then there 
are 3 + 3 + 5 + 4 + 4 = 19 letters used in total.

If all the numbers from 1 to 1000 (one thousand) inclusive were written out in words, 
how many letters would be used? 

NOTE: Do not count spaces or hyphens. For example, 342 (three hundred and forty-two) 
contains 23 letters and 115 (one hundred and fifteen) contains 20 letters. The use of 
"and" when writing out numbers is in compliance with British usage.

Solution Approach:
This solution uses a recursive approach to convert numbers to their word representations:

1. Dictionary-Based Foundation: We begin with a mapping of basic numbers (1-20, tens up to 90)
   to their word representations.

2. Hierarchical Decomposition: Numbers are broken down into manageable chunks:
   - For numbers under 100: We handle direct dictionary lookups or tens-ones combinations
   - For numbers under 1000: We break down into hundreds and remainder parts
   - For larger numbers: We segment into triplets and apply appropriate scale suffixes
     (thousand, million, etc.)

3. British Usage Compliance: We strictly follow British conventions:
   - "and" is included after "hundred" when there's a remainder
   - Proper hyphenation is applied for compound numbers (e.g., twenty-one)

4. Optimization: We use memoization (@lru_cache) to avoid recalculating common number
   representations, significantly improving performance.

5. Letter Counting: Finally, we strip out spaces and hyphens before counting letters
   in accordance with the problem's rules.

The algorithm handles numbers of arbitrary size by decomposing them into triplets
and applying appropriate suffixes, though the problem only requires handling numbers
up to 1000.

Test Cases:
- For max_number=5: 19 letters total
- For max_number=1000: 21124 letters total

URL: https://projecteuler.net/problem=17
Answer: 21124
"""
from functools import lru_cache

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_number': 5}, answer=19, ),
    ProblemArgs(kwargs={'max_number': 1000}, answer=21124, ),
]

# Dictionary mapping basic numbers to their word representations
# Includes single digits, teens, and multiples of 10 up to 90
number_to_word = {
    0: '', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
    18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy',
    80: 'eighty', 90: 'ninety'
}

# Tuple of suffixes for different place values in ascending order
# Each suffix corresponds to a power of 1000 (thousand, million, billion, etc.)
placeholder_suffixes = (
    '', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion', 'septillion',
    'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion', 'tredecillion', 'quatttuor-decillion',
    'quindecillion', 'sexdecillion', 'septen-decillion', 'octodecillion', 'novemdecillion', 'vigintillion', 'centillion'
)

# Suffix used for hundreds place
hundred_suffix = 'hundred'


# In British English, the word "and" is used as a connector between hundred and the rest of the number
# This is enforced in the problem statement: "The use of 'and' when writing out numbers is in compliance with British usage."
# Examples: "one hundred and one", "three hundred and forty-two"


@lru_cache()
def number_triplet_in_words(number: int) -> str:
    """Convert a number from 0-999 to its word representation.

    This function handles three-digit numbers (triplets) by breaking them down
    into hundreds and remaining parts, following British usage rules.
    Memoization is used to improve performance for repeated calculations.

    Args:
        number: A positive integer between 0 and 999

    Returns:
        String representation of the number in words
    """
    number = int(number)
    if number in number_to_word:
        return number_to_word[number]
    elif number < 100:
        return f'{number_to_word[10 * (number // 10)]}-{number_to_word[number % 10]}'
    else:
        hundreds = number // 100
        rest = number % 100
        return f'{number_to_word[hundreds]} {hundred_suffix}{" and " if rest else ""}{number_triplet_in_words(rest)}'


def convert_number_to_words(number: int) -> str:
    """Convert any positive integer to its full word representation.

    This function handles numbers of any size by breaking them into groups of three digits
    (triplets) and applying the appropriate scale suffix (thousand, million, etc.)
    to each group, following British usage conventions.

    The algorithm works as follows:
    1. Split the number into comma-separated triplets (e.g., 1,234,567)
    2. Convert each triplet to words using number_triplet_in_words()
    3. Append the appropriate scale suffix to each triplet (thousand, million, etc.)
    4. Apply British usage rules (e.g., adding 'and' before the final triplet when needed)
    5. Join all parts with spaces to form the complete word representation

    For example, 1,234,567 would be processed as:
    - "one million" (from triplet 1 with suffix 'million')
    - "two hundred and thirty-four thousand" (from triplet 234 with suffix 'thousand')
    - "five hundred and sixty-seven" (from triplet 567 with no suffix)
    Resulting in: "one million two hundred and thirty-four thousand five hundred and sixty-seven"

    Args:
        number: A positive integer to be converted to words

    Returns:
        Complete string representation of the number in words following British conventions
    """
    number_triplets = f'{number:,}'.split(',')
    len_number_triplets = len(number_triplets)
    number_triplet_strings = tuple((number_triplet_in_words(int(s)), placeholder_suffixes[len_number_triplets - i - 1])
                                   for i, s in enumerate(number_triplets))
    number_triplets_in_words = list(f'{s}{" " if p else ""}{p}' for s, p in number_triplet_strings)
    if len_number_triplets > 1 and number_triplets_in_words[-1] and 'and' not in number_triplets_in_words[-1]:
        number_triplets_in_words[-1] = 'and ' + number_triplets_in_words[-1]
    return ' '.join(number_triplets_in_words)


def solution(*, max_number: int) -> int:
    """Calculate the total number of letters used when writing all numbers from 1 to max_number in words.

    Following the problem rules, spaces and hyphens are not counted.
    The function converts each number to words following British usage,
    then counts only the letters by removing spaces and hyphens.

    Algorithm:
    1. For each number from 1 to max_number:
       a. Convert the number to its word representation using convert_number_to_words()
       b. Remove all spaces and hyphens from the word representation
       c. Count the remaining characters (letters only)
    2. Return the sum of all letter counts

    Implementation Note:
    - We use Python's string.translate() method with a mapping table that removes
      spaces and hyphens, which is more efficient than multiple replace() calls
    - The @lru_cache decorator on number_triplet_in_words() significantly improves
      performance by avoiding redundant calculations

    Complexity:
    - Time: O(max_number * log(max_number)) - we process each number and the word length
      grows logarithmically with the number's value
    - Space: O(unique_triplets) - storage for memoized triplet representations

    Args:
        max_number: The upper limit (inclusive) of numbers to convert to words

    Returns:
        Total count of letters used in all word representations

    Example:
        >>> solution(max_number=5)  # "one", "two", "three", "four", "five"
        19  # 3 + 3 + 5 + 4 + 4 = 19 letters total
    """
    ignored_chars = {ord(i): None for i in (' ', '-')}
    return sum(len(convert_number_to_words(s).translate(ignored_chars)) for s in range(1, max_number + 1))


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
