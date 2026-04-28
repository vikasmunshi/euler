#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0022/p0022.py :: solve_names_scores_p0022_s0.

Project Euler Problem 22: Names Scores.

Problem Statement:
    Using names.txt (right click and 'Save Link/Target As...'), a 46K text file
    containing over five-thousand first names, begin by sorting it into
    alphabetical order. Then working out the alphabetical value for each name,
    multiply this value by its alphabetical position in the list to obtain a
    name score.

    For example, when the list is sorted into alphabetical order, COLIN, which
    is worth 3 + 15 + 12 + 9 + 14 = 53, is the 938th name in the list. So,
    COLIN would obtain a score of 938 * 53 = 49714.

    What is the total of all the name scores in the file?

Solution Approach:
    Parse and sort the list of names. Compute alphabetical value for each name
    by summing alphabetical positions of letters. Multiply by the name's
    position in sorted list. Sum all these products. Time complexity O(n log n)
    due to sorting.

Answer: 871198282
URL: https://projecteuler.net/problem=22"""
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


def solve(*, file_url: str) -> int:
    return sum(
        (i * word_to_num(n) for i, n in enumerate(sorted((n for n in get_text_file(file_url).split(','))), start=1)))


if __name__ == '__main__':
    import sys

    print(solve(file_url=str(sys.argv[1])))
