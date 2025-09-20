#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=22
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 22
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0022_names.txt'},
     'answer': 871198282},
]


@lru_cache(maxsize=None)
def word_to_num(word: str) -> int:
    return sum(ord(c) - 64 for c in word.strip('"') if c != ' ')


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_names_scores_p0022_s0(*, file_url: str) -> int:
    return sum((i * word_to_num(n) for i, n in
                enumerate(sorted((n for n in get_text_file(file_url).split(','))), start=1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
