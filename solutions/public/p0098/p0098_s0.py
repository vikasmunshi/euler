#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 98: Anagramic Squares [Level 8]. """
from __future__ import annotations

import collections
import dataclasses
import itertools
import math

from solver.runners import runner


def str_hash(s: str) -> str:
    """Frequency signature: per-character repeat counts sorted descending (a bijection-invariant)."""
    return "".join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagram:
    """One anagram class: a canonical sorted-letter key plus the dictionary words sharing it."""
    canonical: str
    dictionary_words: set[str] = dataclasses.field(default_factory=set)

    @property
    def anagram_length(self) -> int:
        """Word length if this class holds a usable pair (more than one word), else 0."""
        return len(self.canonical) if len(self.dictionary_words) > 1 else 0


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagrams:
    """Anagram classes indexed first by word length, then by canonical sorted-letter key."""
    anagrams: dict[int, dict[str, Anagram]] = dataclasses.field(default_factory=lambda: collections.defaultdict(dict))

    def add_word(self, word: str) -> None:
        """Bucket a word under its length and its canonical (sorted-letter) form."""
        canonical = "".join(sorted(word))
        word_len = len(canonical)
        if canonical not in self.anagrams[word_len]:
            self.anagrams[word_len][canonical] = Anagram(canonical=canonical)
        self.anagrams[word_len][canonical].dictionary_words.add(word)

    def prune(self) -> None:
        """Drop singleton classes and now-empty length groups: they can never form a pair."""
        for word_len in self.anagrams.keys():
            for anagram in list(self.anagrams[word_len].values()):
                if anagram.anagram_length == 0:
                    del self.anagrams[word_len][anagram.canonical]
        for word_len in list(self.anagrams.keys()):
            if len(self.anagrams[word_len]) == 0:
                del self.anagrams[word_len]
        return None


def n_digit_squares(n: int) -> set[str]:
    """All exactly-n-digit perfect squares as strings, scanning roots in [ceil(sqrt(10^(n-1))), floor(sqrt(10^n-1))]."""
    square_numbers: set[str] = set()
    min_sqrt = math.ceil(math.sqrt(10 ** (n - 1)))
    max_sqrt = math.floor(math.sqrt(10**n - 1))
    for i in range(min_sqrt, max_sqrt + 1):
        square_numbers.add(str(i * i))
    return square_numbers


@runner.main
def solve(*args: str) -> str:
    """Group words into anagram classes, then for lengths largest-first match each word to an
    equal-length square via the bijection implied by zipping letters to digits; a class hit at the
    longest length is the maximum. Shape-hash prefiltering prunes incompatible (word, square) pairs;
    cost ~ (anagram words) x (squares per length)."""
    file_url = args[0]

    words: list[str] = runner.get_text_file(file_url).replace('"', "").split(",")
    anagrams: Anagrams = Anagrams()
    for word in words:
        anagrams.add_word(word)
    anagrams.prune()
    for word_length in sorted(anagrams.anagrams.keys(), reverse=True):
        candidates: list[Anagram] = list(anagrams.anagrams.get(word_length, {}).values())
        square_numbers: set[str] = n_digit_squares(word_length)
        for candidate in candidates:
            for word, square_num in itertools.product(candidate.dictionary_words, square_numbers):
                if str_hash(word) != str_hash(square_num):
                    continue
                char_map: dict[str, str] = dict(zip(word, square_num))
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
                    return str(max_square)
    else:
        raise ValueError("No square anagrams found")


if __name__ == "__main__":
    raise SystemExit(solve())
