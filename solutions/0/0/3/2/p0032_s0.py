#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 32: Pandigital Products [Level 2]. """
from __future__ import annotations

import itertools
from sys import argv, stderr
from time import perf_counter
from typing import Any

nine_digits: tuple[str, ...] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
set_nine_digits: set[str] = set(nine_digits)


def is_nine_pandigital(n: int | str) -> bool:
    return len(str(n)) == 9 and set(str(n)) == set_nine_digits


def solve() -> int:
    return sum(
        set(
            (
                c
                for a_len, b_len in ((1, 4), (2, 3))
                for a in itertools.permutations(nine_digits, a_len)
                for b in itertools.permutations((d for d in nine_digits if d not in a), b_len)
                if is_nine_pandigital(
                    (a_str := "".join(a)) + (b_str := "".join(b)) + str((c := (int(a_str) * int(b_str))))
                )
            )
        )
    )


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
    raise SystemExit(main())
