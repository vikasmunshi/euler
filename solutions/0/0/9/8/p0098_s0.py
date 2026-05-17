#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 98: Anagramic Squares [Level 8]. """
from __future__ import annotations

import collections
import dataclasses
import itertools
import math
from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources/" + src.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def str_hash(s: str) -> str:
    return "".join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagram:
    canonical: str
    dictionary_words: set[str] = dataclasses.field(default_factory=set)

    @property
    def anagram_length(self) -> int:
        return len(self.canonical) if len(self.dictionary_words) > 1 else 0


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True)
class Anagrams:
    anagrams: dict[int, dict[str, Anagram]] = dataclasses.field(default_factory=lambda: collections.defaultdict(dict))

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


def n_digit_squares(n: int) -> set[str]:
    square_numbers: set[str] = set()
    min_sqrt = math.ceil(math.sqrt(10 ** (n - 1)))
    max_sqrt = math.floor(math.sqrt(10**n - 1))
    for i in range(min_sqrt, max_sqrt + 1):
        square_numbers.add(str(i * i))
    return square_numbers


def solve(*, file_url: str) -> int:
    words: list[str] = get_text_file(file_url).replace('"', "").split(",")
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
                    return max_square
    else:
        raise ValueError("No square anagrams found")


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(file_url=str(argv[1])))
