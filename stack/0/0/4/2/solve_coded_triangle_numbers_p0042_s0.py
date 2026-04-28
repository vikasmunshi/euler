#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0042/p0042.py :: solve_coded_triangle_numbers_p0042_s0.

Project Euler Problem 42: Coded Triangle Numbers.

Problem Statement:
    The nth term of the sequence of triangle numbers is given by, t_n = 1/2 n (n+1);
    so the first ten triangle numbers are:
    1, 3, 6, 10, 15, 21, 28, 36, 45, 55, ...

    By converting each letter in a word to a number corresponding to its alphabetical
    position and adding these values we form a word value. For example, the word value
    for SKY is 19 + 11 + 25 = 55 = t_10. If the word value is a triangle number then
    we shall call the word a triangle word.

    Using words.txt, a 16K text file containing nearly two-thousand common English words,
    how many are triangle words?

Solution Approach:
    Precompute triangle numbers up to a maximum word value (based on word length and letter
    scores). Convert each word to its value by summing letter positions.
    Check if the word value is one of the precomputed triangle numbers.
    Count how many words qualify. Use set membership for O(1) lookup. Expected complexity
    is O(W * L) where W is number of words and L is max word length.

Answer: 162
URL: https://projecteuler.net/problem=42"""
from __future__ import annotations

from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=None)
def word_to_num(word: str) -> int:
    return sum((ord(c) - 64 for c in word.strip('"') if c != ' '))


def get_text_file(url: str) -> str:
    """ Return the contents of a file from the 'resources' directory. """
    local_filename: str = 'resources' + '/' + url.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


def is_triangle_number(n: int) -> bool:
    result: bool = ((8 * n + 1) ** 0.5).is_integer()
    return result


def solve(*, file_url: str) -> int:
    return sum((is_triangle_number(word_to_num(word)) for word in get_text_file(file_url).split(',')))


if __name__ == '__main__':
    import sys

    print(solve(file_url=str(sys.argv[1])))
