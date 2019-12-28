#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=22
Using names.txt (right click and 'Save Link/Target As...'), a 46K text file containing over five-thousand first names,
begin by sorting it into alphabetical order. Then working out the alphabetical value for each name, multiply this value
by its alphabetical position in the list to obtain a name score.

For example, when the list is sorted into alphabetical order, COLIN, which is worth 3 + 15 + 12 + 9 + 14 = 53,
is the 938th name in the list. So, COLIN would obtain a score of 938 × 53 = 49714.

What is the total of all the name scores in the file?
Answer: 871198282
"""


def total_names_score(filename: str) -> int:
    with open(filename, 'r') as fn:
        names = [n.strip('"').upper() for n in fn.read().split(',')]

    return sum((i + 1) * sum(ord(c) - 64 for c in name) for i, name in enumerate(sorted(names)))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate(total_names_score)(filename='p022_names.txt', answer=871198282)
