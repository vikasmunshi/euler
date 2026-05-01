#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0098/p0098.py
  func: solve_anagramic_squares_p0098_s0
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product
from math import ceil, floor, sqrt
from pathlib import Path
from sys import argv
from typing import Dict, List, Set


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


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
        canonical = "".join(sorted(word))
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


def n_digit_squares(n: int) -> Set[str]:
    square_numbers: Set[str] = set()
    min_sqrt = ceil(sqrt(10 ** (n - 1)))
    max_sqrt = floor(sqrt(10**n - 1))
    for i in range(min_sqrt, max_sqrt + 1):
        square_numbers.add(str(i * i))
    return square_numbers


def str_hash(s: str) -> str:
    return "".join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))


def solve(*, file_url: str) -> int:
    words: list[str] = get_text_file(file_url).replace('"', "").split(",")
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
                word_num: str = "".join((char_map[c] for c in word))
                if word_num not in square_numbers:
                    continue
                max_square: int = 0
                for other_word in candidate.dictionary_words - {word}:
                    other_word_num = "".join((char_map[c] for c in other_word))
                    if other_word_num in square_numbers:
                        max_square = max(max_square, int(word_num), int(other_word_num))
                if max_square > 0:
                    return max_square
    else:
        raise ValueError("No square anagrams found")


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
