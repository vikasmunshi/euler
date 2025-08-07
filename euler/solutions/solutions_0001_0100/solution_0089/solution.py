#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 89: Roman Numerals.

  Problem Statement:
    For a number written in Roman numerals to be considered valid there are basic
    rules which must be followed. Even though the rules allow some numbers to be
    expressed in more than one way there is always a "best" way of writing a
    particular number.

    For example, it would appear that there are at least six ways of writing the
    number sixteen:

        IIIIIIIIIIIIIIII
        VIIIIIIIIIII
        VVIIIIII
        XIIIIII
        VVVI
        XVI

    However, according to the rules only XIIIIII and XVI are valid, and the last
    example is considered to be the most efficient, as it uses the least number
    of numerals.

    The 11K text file, roman.txt (right click and 'Save Link/Target As...'),
    contains one thousand numbers written in valid, but not necessarily minimal,
    Roman numerals; see About... Roman Numerals for the definitive rules for
    this problem.

    Find the number of characters saved by writing each of these in their
    minimal form.

    Note: You can assume that all the Roman numerals in the file contain no more
    than four consecutive identical units.

  Solution Approach:
    To solve this problem, start by understanding and implementing the rules
    governing valid Roman numerals and how to convert them into their minimal
    form. Read the provided text file containing Roman numerals and for each
    numeral, convert it to an integer value.

    Next, design a conversion method to transform this integer back into the
    minimal Roman numeral representation according to the standard rules.
    Compare the lengths of the original and the minimal forms to calculate the
    number of characters saved.

    Efficient string processing and a clear mapping between integers and Roman
    numerals are essential. Careful handling of subtractive combinations like
    IV and IX will be key for correct minimal forms.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0089_roman.txt,
      answer=743.


  Answer: 743
  URL: https://projecteuler.net/problem=89
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.setup.cached_requests import get_text_file
from euler.utils.roman_numerals import number_as_roman_numeral, roman_to_number


@register_solution(euler_problem=89, test_case_category=TestCaseCategory.EXTENDED)
def roman_numerals(*, file_url: str) -> int:
    characters_saved: int = 0
    for numeral in get_text_file(file_url).splitlines(keepends=False):
        minimal_form = number_as_roman_numeral(roman_to_number(numeral))
        characters_saved += len(numeral) - len(minimal_form)
    return characters_saved


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=89, time_out_in_seconds=300, mode='evaluate'))
