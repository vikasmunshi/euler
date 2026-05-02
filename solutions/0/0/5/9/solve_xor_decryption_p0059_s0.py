#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0059/p0059.py
  func: solve_xor_decryption_p0059_s0
"""

from __future__ import annotations

from pathlib import Path
from sys import argv
from typing import List, Tuple


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def show_solution() -> bool:
    return "--show" in argv


def solve(*, file_url: str, key_length: int, most_common_letters: str) -> int:
    encrypted: List[int] = [int(x) for x in get_text_file(file_url).split(",")]
    slices_range: Tuple[int, ...] = tuple(range(key_length))
    encrypted_slices: List[List[int]] = [encrypted[i::key_length] for i in slices_range]
    key: List[int] = [0] * key_length
    score: List[int] = [0] * key_length
    decrypted: List[str] = [""] * key_length
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = "".join((chr(_char ^ _key) for _char in encrypted_slices[i]))
            if (_score := sum((_decrypted.count(x) for x in most_common_letters))) > score[i]:
                score[i], key[i], decrypted[i] = (_score, _key, _decrypted)
    if show_solution():
        print("".join(("".join(chars) for chars in zip(*decrypted))))
    return sum((ord(_char) for _decrypted in decrypted for _char in _decrypted))


def main() -> int:
    print(solve(file_url=str(argv[1]), key_length=int(argv[2]), most_common_letters=str(argv[3])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
