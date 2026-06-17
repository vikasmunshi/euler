#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 59: XOR Decryption [Level 1]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Break repeating-key XOR by splitting the ciphertext into key_length interleaved single-byte
    XOR slices and picking, per slice, the lowercase key byte whose decryption has the most common
    letters; this collapses a 26^k search into k linear scans: O(26 * n)."""
    file_url = args[0]
    key_length = runner.parse_int(args[1])
    most_common_letters = args[2]

    encrypted: list[int] = [int(x) for x in runner.get_text_file(file_url).split(",")]
    slices_range: tuple[int, ...] = tuple(range(key_length))
    # Slice i holds ciphertext bytes at positions i, i+k, i+2k, ... - each a single-byte XOR cipher.
    encrypted_slices: list[list[int]] = [encrypted[i::key_length] for i in slices_range]
    key: list[int] = [0] * key_length
    score: list[int] = [0] * key_length
    decrypted: list[str] = [""] * key_length
    # For each lowercase candidate byte, keep per slice the one maximising common-letter occurrences.
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = "".join((chr(_char ^ _key) for _char in encrypted_slices[i]))
            if (_score := sum((_decrypted.count(x) for x in most_common_letters))) > score[i]:
                score[i], key[i], decrypted[i] = (_score, _key, _decrypted)
    if runner.show:
        print("".join(("".join(chars) for chars in zip(*decrypted))))
    return str(sum((ord(_char) for _decrypted in decrypted for _char in _decrypted)))


if __name__ == "__main__":
    raise SystemExit(solve())
