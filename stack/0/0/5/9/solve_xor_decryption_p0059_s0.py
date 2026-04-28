#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0059/p0059.py :: solve_xor_decryption_p0059_s0.

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
URL: https://projecteuler.net/problem=59"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple


def show_solution() -> bool:
    return '--show' in sys.argv


def get_text_file(url: str) -> str:
    """ Return the contents of a file from the 'resources' directory. """
    local_filename: str = 'resources' + '/' + url.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str, key_length: int, most_common_letters: str) -> int:
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
        print(''.join((''.join(chars) for chars in zip(*decrypted))), file=sys.stderr)
    return sum((ord(_char) for _decrypted in decrypted for _char in _decrypted))


if __name__ == '__main__':
    print(solve(file_url=str(sys.argv[1]), key_length=int(sys.argv[2]), most_common_letters=str(sys.argv[3])))
