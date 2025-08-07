#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 42: Coded Triangle Numbers.

  Problem Statement:
    The n th term of the sequence of triangle numbers is given by, t_n = 1/2 n(n+1); so
    the first ten triangle numbers are:
    1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...

    By converting each letter in a word to a number corresponding to its alphabetical
    position and adding these values we form a word value. For example, the word
    value for SKY is 19 + 11 + 25 = 55 = t_10. If the word value is a triangle number
    then we shall call the word a triangle word.

    Using words.txt (right click and 'Save Link/Target As...'), a 16K text file
    containing nearly two-thousand common English words, how many are triangle words?

  Solution Approach:
    To solve this problem, first generate a list of triangle numbers up to the
    maximum possible word value. Next, read the provided list of words and convert
    each word to its word value by summing the alphabetical positions of its letters
    (A=1, B=2, ...). Check if each word value is present in the list of triangle
    numbers. Counting all such occurrences gives the number of triangle words.

    Efficient string processing and precomputation of triangle numbers will be
    key. Consider using a set for quick membership checking of triangle numbers.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0042_words.txt,
      answer=162.


  Answer: 162
  URL: https://projecteuler.net/problem=42
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.setup.cached_requests import get_text_file
from euler.utils.word_to_num import word_to_num


@register_solution(euler_problem=42, test_case_category=TestCaseCategory.EXTENDED)
def coded_triangle_numbers(*, file_url: str) -> int:
    return sum((is_triangle_number(word_to_num(word)) for word in get_text_file(file_url).split(',')))


def is_triangle_number(n: int) -> bool:
    result: bool = ((8 * n + 1) ** 0.5).is_integer()
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=42, time_out_in_seconds=300, mode='evaluate'))
