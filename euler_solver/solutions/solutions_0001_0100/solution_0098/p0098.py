#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 98: Anagramic Squares.

Problem Statement:
    By replacing each of the letters in the word CARE with 1, 2, 9, and 6 respectively,
    we form a square number: 1296 = 36^2. What is remarkable is that, by using the same
    digital substitutions, the anagram, RACE, also forms a square number: 9216 = 96^2.
    We shall call CARE (and RACE) a square anagram word pair and specify further that
    leading zeroes are not permitted, neither may a different letter have the same
    digital value as another letter.

    Using words.txt (right click and 'Save Link/Target As...'), a 16K text file containing
    nearly two-thousand common English words, find all the square anagram word pairs
    (a palindromic word is NOT considered to be an anagram of itself).

    What is the largest square number formed by any member of such a pair?

    NOTE: All anagrams formed must be contained in the given text file.

Solution Approach:
    Use combinatorics and hashing to find anagram pairs among the words. For each pair,
    attempt all digit-letter mappings that form one square number and check if the mapping
    produces a square number for the other word. Use a dictionary keyed by sorted word letters
    for efficient anagram grouping. Precompute squares of appropriate lengths to speed lookups.
    Complexity depends on word count and square candidate sets.

Answer: 18769
URL: https://projecteuler.net/problem=98
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product
from math import ceil, floor, sqrt
from typing import Any, Dict, List, Set

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 98
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0098_words.txt'},
     'answer': 18769},
]


@dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagram:
    canonical: str
    dictionary_words: Set[str] = field(default_factory=set)

    @property
    def anagram_length(self) -> int:
        return len(self.canonical) if len(self.dictionary_words) > 1 else 0


@dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagrams:
    anagrams: Dict[int, Dict[str, Anagram]] = field(default_factory=lambda: defaultdict(dict))

    def add_word(self, word: str) -> None:
        canonical = ''.join(sorted(word))
        word_len = len(canonical)
        if canonical not in self.anagrams[word_len]:
            self.anagrams[word_len][canonical] = Anagram(canonical=canonical)
        self.anagrams[word_len][canonical].dictionary_words.add(word)

    def prune(self) -> None:
        for word_len in self.anagrams.keys():
            for anagram in list(self.anagrams[word_len].values()):
                if anagram.anagram_length == 0:
                    del self.anagrams[word_len][anagram.canonical]
        for word_len in list(self.anagrams.keys()):
            if len(self.anagrams[word_len]) == 0:
                del self.anagrams[word_len]
        return None


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_anagramic_squares_p0098_s0(*, file_url: str) -> int:
    words: list[str] = get_text_file(file_url).replace('"', '').split(',')
    anagrams: Anagrams = Anagrams()
    for word in words:
        anagrams.add_word(word)
    anagrams.prune()
    for word_length in sorted(anagrams.anagrams.keys(), reverse=True):
        candidates: List[Anagram] = list(anagrams.anagrams.get(word_length, {}).values())
        square_numbers: Set[str] = n_digit_squares(word_length)
        for candidate in candidates:
            for word, square_num in product(candidate.dictionary_words, square_numbers):
                if str_hash(word) != str_hash(square_num):
                    continue
                char_map: Dict[str, str] = dict(zip(word, square_num))
                if len(char_map) != len(word):
                    continue
                if len(set(char_map.values())) != len(char_map):
                    continue
                word_num: str = ''.join((char_map[c] for c in word))
                if word_num not in square_numbers:
                    continue
                max_square: int = 0
                for other_word in candidate.dictionary_words - {word}:
                    other_word_num = ''.join((char_map[c] for c in other_word))
                    if other_word_num in square_numbers:
                        max_square = max(max_square, int(word_num), int(other_word_num))
                if max_square > 0:
                    return max_square
    else:
        raise ValueError('No square anagrams found')


def n_digit_squares(n: int) -> Set[str]:
    square_numbers: Set[str] = set()
    min_sqrt = ceil(sqrt(10 ** (n - 1)))
    max_sqrt = floor(sqrt(10 ** n - 1))
    for i in range(min_sqrt, max_sqrt + 1):
        square_numbers.add(str(i * i))
    return square_numbers


def str_hash(s: str) -> str:
    return ''.join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
