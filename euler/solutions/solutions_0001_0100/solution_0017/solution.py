#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 17: Number Letter Counts.

  Problem Statement:
    If the numbers 1 to 5 are written out in words: one, two, three, four, five, then
    there are 3 + 3 + 5 + 4 + 4 = 19 letters used in total.

    If all the numbers from 1 to 1000 (one thousand) inclusive were written out in words,
    how many letters would be used?

    Note:
    Do not count spaces or hyphens. For example, 342 (three hundred and forty two)
    contains 23 letters and 115 (one hundred and fifteen) contains 20 letters. The use
    of "and" when writing out numbers is in compliance with British usage.

  Solution Approach:
    To solve this problem, first devise a function to convert integers into their
    English word equivalents, carefully following British usage, including the correct
    use of "and" between hundreds and tens/units. Avoid counting spaces or hyphens
    when tallying letters. Then programmatically generate words for all numbers from 1
    through 1000, compute the total letter count of these word representations, and
    output the sum. This approach requires precise string manipulation, indexing of
    number words, and iterating through the numeric range.

  Test Cases:
    preliminary:
      max_number=5,
      answer=19.

    main:
      max_number=1000,
      answer=21124.


  Answer: 21124
  URL: https://projecteuler.net/problem=17
"""
from __future__ import annotations

from functools import lru_cache

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution

number_to_word = {0: '', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
                  9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen',
                  16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty',
                  40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'}
placeholder_suffixes = ('', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion',
                        'septillion', 'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion',
                        'tredecillion', 'quatttuor-decillion', 'quindecillion', 'sexdecillion', 'septen-decillion',
                        'octodecillion', 'novemdecillion', 'vigintillion', 'centillion')
hundred_suffix = 'hundred'


@lru_cache()
def number_triplet_in_words(number: int) -> str:
    number = int(number)
    if number in number_to_word:
        return number_to_word[number]
    elif number < 100:
        return f'{number_to_word[10 * (number // 10)]}-{number_to_word[number % 10]}'
    else:
        hundreds = number // 100
        rest = number % 100
        return f'{number_to_word[hundreds]} {hundred_suffix}{(' and ' if rest else '')}{number_triplet_in_words(rest)}'


def convert_number_to_words(number: int) -> str:
    number_triplets = f'{number:,}'.split(',')
    len_number_triplets = len(number_triplets)
    number_triplet_strings = tuple(
            ((number_triplet_in_words(int(s)), placeholder_suffixes[len_number_triplets - i - 1]) for i, s in
             enumerate(number_triplets)))
    number_triplets_in_words = list((f'{s}{(' ' if p else '')}{p}' for s, p in number_triplet_strings))
    if len_number_triplets > 1 and number_triplets_in_words[-1] and ('and' not in number_triplets_in_words[-1]):
        number_triplets_in_words[-1] = 'and ' + number_triplets_in_words[-1]
    return ' '.join(number_triplets_in_words)


@register_solution(euler_problem=17, test_case_category=TestCaseCategory.EXTENDED)
def number_letter_counts(*, max_number: int) -> int:
    ignored_chars = {ord(i): None for i in (' ', '-')}
    return sum((len(convert_number_to_words(s).translate(ignored_chars)) for s in range(1, max_number + 1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=17, time_out_in_seconds=300, mode='evaluate'))
