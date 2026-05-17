#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 43: Sub-string Divisibility [Level 1]. """
from __future__ import annotations

import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any, Generator


def solve() -> int:
    valid_multiples_of_17 = (
        "017",
        "034",
        "051",
        "068",
        "085",
        "102",
        "136",
        "153",
        "170",
        "187",
        "204",
        "238",
        "289",
        "306",
        "340",
        "357",
        "374",
        "391",
        "408",
        "425",
        "459",
        "476",
        "493",
        "510",
        "527",
        "561",
        "578",
        "612",
        "629",
        "680",
        "697",
        "714",
        "731",
        "748",
        "765",
        "782",
        "816",
        "850",
        "867",
        "901",
        "918",
        "935",
        "952",
        "986",
    )

    def gen_special_numbers(current_number: str | None = None, divisor: int = 17) -> Generator[int, None, None]:
        next_divisor: int | None = {3: 2, 5: 3, 7: 5, 11: 7, 13: 11, 17: 13}.get(divisor, None)
        if current_number is None:
            for num_str in valid_multiples_of_17:
                yield from gen_special_numbers(current_number=num_str, divisor=next_divisor)
        else:
            for next_digit in (d for d in "0123456789" if d not in current_number):
                next_num: str = next_digit + current_number
                if int(next_num[:3]) % divisor != 0:
                    continue
                if next_divisor is None:
                    yield int(next((d for d in "0123456789" if d not in next_num)) + next_num)
                else:
                    yield from gen_special_numbers(current_number=next_num, divisor=next_divisor)

    if sys.argv[-1] == "--show":
        result: int = 0
        for num in gen_special_numbers():
            result += num
            print(num)
        return result
    return sum((num for num in gen_special_numbers()))


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
