#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 22: Names Scores.

  Problem Statement:
    Using names.txt (right click and 'Save Link/Target As...'), a 46K text file
    containing over five-thousand first names, begin by sorting it into
    alphabetical order. Then working out the alphabetical value for each name,
    multiply this value by its alphabetical position in the list to obtain a
    name score.

    For example, when the list is sorted into alphabetical order, COLIN, which
    is worth 3 + 15 + 12 + 9 + 14 = 53, is the 938th name in the list. So,
    COLIN would obtain a score of 938 x 53 = 49714.

    What is the total of all the name scores in the file?

  Solution Approach:
    To solve this problem, first download and read the names text file. Parse
    the names into a list and sort them alphabetically. For each name, compute
    its alphabetical value by summing the positions of its letters in the
    alphabet (A=1, B=2, etc.). Multiply this value by the name's position in
    the sorted list to get the name score. Finally, sum all the name scores to
    find the total. Efficient string processing and proper sorting algorithms
    are key.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0022_names.txt,
      answer=871198282.


  Answer: 871198282
  URL: https://projecteuler.net/problem=22
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.setup.cached_requests import get_text_file
from euler.utils.word_to_num import word_to_num


@register_solution(euler_problem=22, test_case_category=TestCaseCategory.EXTENDED)
def names_scores(*, file_url: str) -> int:
    return sum((i * word_to_num(n) for i, n in
                enumerate(sorted((n for n in get_text_file(file_url).split(','))), start=1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=22, time_out_in_seconds=300, mode='evaluate'))
