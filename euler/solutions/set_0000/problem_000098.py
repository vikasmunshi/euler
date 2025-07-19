#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 98:

Problem Statement:
By replacing each of the letters in the word CARE with 1, 2, 9, and 6 respectively, we form a square number: 1296 = 36².
What is remarkable is that, by using the same digital substitutions, the anagram, RACE, also forms a square number:
9216 = 96². We shall call CARE (and RACE) a square anagram word pair and specify further that leading zeroes are not
permitted, neither may a different letter have the same digital value as another letter.

Using words.txt (right click and 'Save Link/Target As...'), a 16K text file containing nearly two-thousand common
English words, find all the square anagram word pairs (a palindromic word is NOT considered to be an anagram of itself).

What is the largest square number formed by any member of such a pair?

NOTE: All anagrams formed must be contained in the given text file.

Solution Approach:

This solution finds anagram pairs among words in the provided file and checks if
they can form square numbers using the same letter-to-digit mapping. The steps are:
1. Load words from the file and identify anagram pairs
2. For each anagram pair, generate all square numbers with the same digit length
3. For each word in an anagram pair, try mapping its letters to digits of a square number
4. Check if the mapped digits form another square number when applied to the anagram
5. Return the largest square number found

Test Cases:

URL: https://projecteuler.net/problem=98
Answer: 18769
"""
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product
from math import ceil, floor, sqrt
from typing import Dict, List, Set

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=98)
problem_number: int = 98

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0098_words.txt'}, answer=18769, ),
]


@dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True, )
class Anagram:
    """
    Represents an anagram group with a canonical form and all words that match it.

    Attributes:
        canonical: Sorted string representation of the anagram (e.g., 'acde' for 'cade')
        dictionary_words: Set of all words that are anagrams of the canonical form
    """
    canonical: str
    dictionary_words: Set[str] = field(default_factory=set)

    @property
    def anagram_length(self) -> int:
        """
        Returns the length of the anagram if it has multiple dictionary words,
        otherwise returns 0 (indicating it's not a valid anagram group).

        Returns:
            int: Length of canonical form if multiple words exist, 0 otherwise
        """
        return len(self.canonical) if len(self.dictionary_words) > 1 else 0


@dataclass(frozen=True, slots=True, kw_only=True, eq=True, order=True, unsafe_hash=False, repr=True, )
class Anagrams:
    """
    Collection of anagram groups organized by word length.

    Attributes:
        anagrams: Dictionary mapping word length to another dictionary
                 that maps canonical forms to Anagram objects
    """
    anagrams: Dict[int, Dict[str, Anagram]] = field(default_factory=lambda: defaultdict(dict))

    def add_word(self, word: str) -> None:
        """
        Add a word to the appropriate anagram group based on its sorted letters.

        Args:
            word: The word to be added to an anagram group
        """
        canonical = ''.join(sorted(word))
        word_len = len(canonical)
        if canonical not in self.anagrams[word_len]:
            self.anagrams[word_len][canonical] = Anagram(canonical=canonical)
        self.anagrams[word_len][canonical].dictionary_words.add(word)

    def prune(self) -> None:
        """
        Remove any anagram groups that don't contain multiple words.

        This eliminates words that don't have anagrams in the dictionary
        and empty word length categories, optimizing subsequent processing.
        """
        for word_len in self.anagrams.keys():
            for anagram in list(self.anagrams[word_len].values()):
                if anagram.anagram_length == 0:
                    del self.anagrams[word_len][anagram.canonical]
        for word_len in list(self.anagrams.keys()):
            if len(self.anagrams[word_len]) == 0:
                del self.anagrams[word_len]
        return None


def n_digit_squares(n: int) -> Set[str]:
    """Generate all n-digit square numbers."""
    square_numbers: Set[str] = set()
    # Calculate the range boundaries more precisely
    min_sqrt = ceil(sqrt(10 ** (n - 1)))
    max_sqrt = floor(sqrt(10 ** n - 1))

    for i in range(min_sqrt, max_sqrt + 1):
        square_numbers.add(str(i * i))
    return square_numbers


def str_hash(s: str) -> str:
    """Create a hash for string pattern matching.

    Returns a string representing the frequency pattern of characters.
    Two strings with the same character frequency distribution will have the same hash.
    """
    return ''.join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))


# Register this function as a solution for problem #98 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def largest_square_anagram_word_pairs(*, file_url: str) -> int:
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
                # Map each letter to a digit, ensuring a one-to-one mapping
                char_map: Dict[str, str] = dict(zip(word, square_num))
                # Verify all letters have unique digit values
                if len(char_map) != len(word):
                    continue
                # Ensure the mapping is one-to-one (no two letters map to the same digit)
                if len(set(char_map.values())) != len(char_map):
                    continue

                word_num: str = ''.join(char_map[c] for c in word)
                if word_num not in square_numbers:
                    continue
                max_square: int = 0
                for other_word in candidate.dictionary_words - {word}:
                    other_word_num = ''.join(char_map[c] for c in other_word)
                    if other_word_num in square_numbers:
                        max_square = max(max_square, int(word_num), int(other_word_num))
                if max_square > 0:
                    return max_square
    else:
        raise ValueError('No square anagrams found')


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
