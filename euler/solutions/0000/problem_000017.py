#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 17 - Number letter counts
# https://projecteuler.net/problem=17
# Answer: answers={5: 19, 1000: 21124}
# Notes: Uses a recursive approach with memoization for converting numbers to words following British usage
import textwrap
from functools import lru_cache

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_number': 5},
        answer=19,
    ),
    ProblemArgs(
        kwargs={'max_number': 1000},
        answer=21124,
    ),
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

    Args:
        number: A positive integer

    Returns:
        Complete string representation of the number in words
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

    Args:
        max_number: The upper limit (inclusive) of numbers to convert to words

    Returns:
        Total count of letters used in all word representations
    """
    ignored_chars = {ord(i): None for i in (' ', '-')}
    return sum(len(convert_number_to_words(s).translate(ignored_chars)) for s in range(1, max_number + 1))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 17: Number letter counts
https://projecteuler.net/problem=17

Problem Description:
If the numbers 1 to 5 are written out in words: one, two, three, four, five,
then there are 3 + 3 + 5 + 4 + 4 = 19 letters used in total.

If all the numbers from 1 to 1000 (one thousand) inclusive were written out in words, how many letters would be used? 

NOTE: Do not count spaces or hyphens. For example, 342 (three hundred and forty-two) contains 23 letters 
and 115 (one hundred and fifteen) contains 20 letters.
The use of "and" when writing out numbers is in compliance with British usage.

Solution Approach:
- Define mappings from numbers to their word representations
- Implement a recursive function to convert three-digit numbers to words
- Handle larger numbers by breaking them into groups of three digits
- Apply appropriate scale suffixes (thousand, million, etc.)
- Follow British usage rules (including "and" between hundreds and tens/units)
- Count only letters by removing spaces and hyphens
- Sum the letter counts across all numbers in the required range

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
