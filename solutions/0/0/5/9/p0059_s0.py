#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 59: XOR Decryption [Level 1]. """
from __future__ import annotations

import sys
from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources/" + src.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str, key_length: int, most_common_letters: str) -> int:
    encrypted: list[int] = [int(x) for x in get_text_file(file_url).split(",")]
    slices_range: tuple[int, ...] = tuple(range(key_length))
    encrypted_slices: list[list[int]] = [encrypted[i::key_length] for i in slices_range]
    key: list[int] = [0] * key_length
    score: list[int] = [0] * key_length
    decrypted: list[str] = [""] * key_length
    for _key in range(97, 123):
        for i in slices_range:
            _decrypted = "".join((chr(_char ^ _key) for _char in encrypted_slices[i]))
            if (_score := sum((_decrypted.count(x) for x in most_common_letters))) > score[i]:
                score[i], key[i], decrypted[i] = (_score, _key, _decrypted)
    if sys.argv[-1] == "--show":
        print("".join(("".join(chars) for chars in zip(*decrypted))))
    return sum((ord(_char) for _decrypted in decrypted for _char in _decrypted))


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
    raise SystemExit(main(file_url=str(argv[1]), key_length=int(argv[2]), most_common_letters=str(argv[3])))
