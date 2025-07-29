#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 89: roman_numerals

Problem Statement:
  For a number written in Roman numerals to be considered valid there are basic
  rules which must be followed. Even though the rules allow some numbers to be
  expressed in more than one way there is always a "best" way of writing a
  particular number. For example, it would appear that there are at least six ways
  of writing the number sixteen: IIIIIIIIIIIIIIII VIIIIIIIIIII VVIIIIII XIIIIII
  VVVI XVI However, according to the rules only XIIIIII and XVI are valid, and the
  last example is considered to be the most efficient, as it uses the least number
  of numerals. The 11K text file, roman.txt (right click and 'Save Link/Target
  As...'), contains one thousand numbers written in valid, but not necessarily
  minimal, Roman numerals; see About... Roman Numerals for the definitive rules
  for this problem. Find the number of characters saved by writing each of these
  in their minimal form. Note: You can assume that all the Roman numerals in the
  file contain no more than four consecutive identical units.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=89
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.misc.roman_numerals import number_as_roman_numeral, roman_to_number
from euler.setup import TestCase
from euler.setup.cached_requests import get_text_file

test_cases: list[TestCase] = [
    TestCase(
        answer=743,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0089_roman.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #89
@register_solution(problem_number=89, test_cases=test_cases)
def roman_numerals(*, file_url: str) -> int:
    """
    Calculate the number of characters saved by converting Roman numerals to their minimal form.

    For each Roman numeral in the input file, this function:
    1. Converts it to its decimal value using roman_to_number
    2. Converts the decimal value back to minimal Roman numeral form using number_as_roman_numeral
    3. Calculates and accumulates the difference in string length

    Args:
        file_url (str): URL to the text file containing Roman numerals, one per line

    Returns:
        int: The total number of characters saved by using minimal forms
    """
    characters_saved: int = 0
    # Process each Roman numeral in the file
    for numeral in get_text_file(file_url).splitlines(keepends=False):
        # Calculate the difference between original and minimal representation lengths
        minimal_form = number_as_roman_numeral(roman_to_number(numeral))
        characters_saved += len(numeral) - len(minimal_form)
    return characters_saved


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(89))
