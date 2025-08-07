#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 59: Xor Decryption.

  Problem Statement:
    Each character on a computer is assigned a unique code and the preferred
    standard is ASCII (American Standard Code for Information Interchange). For
    example, uppercase A = 65, asterisk (*) = 42, and lowercase k = 107.

    A modern encryption method is to take a text file, convert the bytes to
    ASCII, then XOR each byte with a given value, taken from a secret key. The
    advantage with the XOR function is that using the same encryption key on
    the cipher text, restores the plain text; for example, 65 x 42 = 107, then
    107 x 42 = 65.

    For unbreakable encryption, the key is the same length as the plain text
    message, and the key is made up of random bytes. The user would keep the
    encrypted message and the encryption key in different locations, and
    without both "halves", it is impossible to decrypt the message.

    Unfortunately, this method is impractical for most users, so the modified
    method is to use a password as a key. If the password is shorter than the
    message, which is likely, the key is repeated cyclically throughout the
    message. The balance for this method is using a sufficiently long password
    key for security, but short enough to be memorable.

    Your task has been made easy, as the encryption key consists of three lower
    case characters. Using 0059_cipher.txt (right click and 'Save Link/Target
    As...'), a file containing the encrypted ASCII codes, and the knowledge
    that the plain text must contain common English words, decrypt the message
    and find the sum of the ASCII values in the original text.

  Solution Approach:
    To solve this problem, understand the properties of the XOR bitwise
    operation, especially that applying the same key twice restores the original
    text. Since the encryption key is three lowercase ASCII characters, you can
    perform a brute-force search over all 17,576 possible three-character
    keys (from 'aaa' to 'zzz').

    For each key candidate, XOR the encrypted ASCII codes cyclically with the key
    characters and check if the resulting text contains common English words or
    prints readable English. Once you identify readable decryptions, calculate
    and return the sum of the ASCII values of the decrypted text.

    This approach combines cryptanalysis heuristics like language frequency with
    exhaustive trial of limited keyspace, allowing effective decryption.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0059_cipher.txt,
      key_length=9,
      most_common_letters=eEaAnNtT,
      answer=129448.


  Answer: 129448
  URL: https://projecteuler.net/problem=59
"""
from __future__ import annotations

from typing import List, Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution
from euler.setup.cached_requests import get_text_file


@register_solution(euler_problem=59, test_case_category=TestCaseCategory.EXTENDED)
def xor_decryption(*, file_url: str, key_length: int, most_common_letters: str) -> int:
    encrypted: List[int] = [int(x) for x in get_text_file(file_url).split(',')]
    slices_range: Tuple[int, ...] = tuple(range(key_length))
    encrypted_slices: List[List[int]] = [encrypted[i::key_length] for i in slices_range]
    key: List[int] = [0] * key_length
    score: List[int] = [0] * key_length
    decrypted: List[str] = [''] * key_length
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = ''.join((chr(_char ^ _key) for _char in encrypted_slices[i]))
            if (_score := sum((_decrypted.count(x) for x in most_common_letters))) > score[i]:
                score[i], key[i], decrypted[i] = (_score, _key, _decrypted)
    if show_solution():
        print(''.join((''.join(chars) for chars in zip(*decrypted))))
    return sum((ord(_char) for _decrypted in decrypted for _char in _decrypted))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=59, time_out_in_seconds=300, mode='evaluate'))
