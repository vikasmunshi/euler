#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 59: xor_decryption

Problem Statement:
  Each character on a computer is assigned a unique code and the preferred
  standard is ASCII (American Standard Code for Information Interchange). For
  example, uppercase A = 65, asterisk (*) = 42, and lowercase k = 107. A modern
  encryption method is to take a text file, convert the bytes to ASCII, then XOR
  each byte with a given value, taken from a secret key. The advantage with the
  XOR function is that using the same encryption key on the cipher text, restores
  the plain text; for example, 65 XOR 42 = 107, then 107 XOR 42 = 65. For
  unbreakable encryption, the key is the same length as the plain text message,
  and the key is made up of random bytes. The user would keep the encrypted
  message and the encryption key in different locations, and without both
  "halves", it is impossible to decrypt the message. Unfortunately, this method is
  impractical for most users, so the modified method is to use a password as a
  key. If the password is shorter than the message, which is likely, the key is
  repeated cyclically throughout the message. The balance for this method is using
  a sufficiently long password key for security, but short enough to be memorable.
  Your task has been made easy, as the encryption key consists of three lower case
  characters. Using 0059_cipher.txt (right click and 'Save Link/Target As...'), a
  file containing the encrypted ASCII codes, and the knowledge that the plain text
  must contain common English words, decrypt the message and find the sum of the
  ASCII values in the original text.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=59
Answer: None
"""
from __future__ import annotations

from typing import List, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase
from euler.setup.cached_requests import get_text_file

test_cases: list[TestCase] = [
    TestCase(
        answer=129448,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0059_cipher.txt', 'key_length': 9,
                'most_common_letters': 'eEaAnNtT'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #59
@register_solution(problem_number=59, test_cases=test_cases)
def xor_decryption(*, file_url: str, key_length: int, most_common_letters: str) -> int:
    """
    Decrypt an XOR-encrypted message and return the sum of ASCII values in the original text.

    This solution uses frequency analysis to break the XOR encryption. It works by:
    1. Dividing the encrypted text into slices based on the key length
    2. For each slice, trying all lowercase letters as possible key characters
    3. Selecting the key character that produces text with the most common English letters
    4. Combining the results to get the complete decrypted message
    5. Returning the sum of ASCII values in the decrypted text

    Args:
        file_url: URL of the file containing the encrypted ASCII codes
        key_length: The length of the encryption key (3 for this problem)
        most_common_letters: String containing the most common letters in English

    Returns:
        The sum of ASCII values in the decrypted text

    Example:
        >>> xor_decryption(file_url="https://projecteuler.net/resources/documents/0059_cipher.txt",
        ...          key_length=3,
        ...          most_common_letters="eEaAnNtT")
        129448
    """
    encrypted: List[int] = [int(x) for x in get_text_file(file_url).split(',')]
    slices_range: Tuple[int, ...] = tuple(range(key_length))
    encrypted_slices: List[List[int]] = [encrypted[i::key_length] for i in slices_range]
    key: List[int] = [0] * key_length
    score: List[int] = [0] * key_length
    decrypted: List[str] = [''] * key_length
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = ''.join(chr(_char ^ _key) for _char in encrypted_slices[i])
            if (_score := sum((_decrypted.count(x)) for x in most_common_letters)) > score[i]:
                score[i], key[i], decrypted[i] = _score, _key, _decrypted
    if show_solution():
        print(''.join(''.join(chars) for chars in zip(*decrypted)))
    return sum(ord(_char) for _decrypted in decrypted for _char in _decrypted)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(59))
