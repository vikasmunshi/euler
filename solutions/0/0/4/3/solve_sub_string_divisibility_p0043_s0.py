#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0043/p0043.py
  func: solve_sub_string_divisibility_p0043_s0
"""

from __future__ import annotations

from sys import argv, setrecursionlimit
from typing import Generator


def show_solution() -> bool:
    return "--show" in argv


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

    if show_solution():
        result: int = 0
        for num in gen_special_numbers():
            result += num
            print(num)
        return result
    return sum((num for num in gen_special_numbers()))


def main() -> int:
    setrecursionlimit(10**6)
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
