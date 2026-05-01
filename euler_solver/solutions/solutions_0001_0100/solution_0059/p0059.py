#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 59: XOR Decryption.

Problem Statement:
    Each character on a computer is assigned a unique code and the preferred
    standard is ASCII (American Standard Code for Information Interchange).
    For example, uppercase A = 65, asterisk (*) = 42, and lowercase k = 107.

    A modern encryption method is to take a text file, convert the bytes to ASCII,
    then XOR each byte with a given value, taken from a secret key. The advantage
    with the XOR function is that using the same encryption key on the cipher text,
    restores the plain text; for example, 65 XOR 42 = 107, then 107 XOR 42 = 65.

    For unbreakable encryption, the key is the same length as the plain text
    message, and the key is made up of random bytes. The user would keep the
    encrypted message and the encryption key in different locations, and without
    both "halves", it is impossible to decrypt the message.

    Unfortunately, this method is impractical for most users, so the modified
    method is to use a password as a key. If the password is shorter than the
    message, which is likely, the key is repeated cyclically throughout the message.
    The balance for this method is using a sufficiently long password key for security,
    but short enough to be memorable.

    Your task has been made easy, as the encryption key consists of three lower case
    characters. Using the provided cipher file containing the encrypted ASCII codes,
    and the knowledge that the plain text must contain common English words, decrypt
    the message and find the sum of the ASCII values in the original text.

Solution Approach:
    Brute force all possible 3-character lowercase keys (26^3 = 17576 keys).
    For each key, XOR decrypt the ciphertext cyclically.
    Check decrypted text plausibility using English word frequency or common letter heuristics.
    When the correct plaintext is found, sum its ASCII values.
    Time complexity is manageable due to small key space, using fast XOR operations.

Answer: 129448
URL: https://projecteuler.net/problem=59
"""
from __future__ import annotations

from typing import Any, List, Tuple

from euler_solver.framework import evaluate, get_text_file, logger, register_solution, show_solution

euler_problem: int = 59
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0059_cipher.txt',
                                   'key_length': 9, 'most_common_letters': 'eEaAnNtT'},
     'answer': 129448},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_xor_decryption_p0059_s0(*, file_url: str, key_length: int, most_common_letters: str) -> int:
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
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
