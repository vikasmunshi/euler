#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 43: Sub-string Divisibility [Level 1]. """
from __future__ import annotations

from typing import Generator

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Right-to-left constrained backtracking over the divisor chain 17->13->11->7->5->3->2, seeded
    by the 44 valid d8 d9 d10 windows; overlapping windows prune the search heavily.
    Worst case O(10!), but effectively microseconds."""
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
        """Yield each pandigital with the divisibility property by prepending one digit per step so the
        leading three-digit window is divisible by divisor; seed with the d8 d9 d10 table when called bare."""
        next_divisor: int | None = {3: 2, 5: 3, 7: 5, 11: 7, 13: 11, 17: 13}.get(divisor, None)
        if current_number is None:
            for num_str in valid_multiples_of_17:
                yield from gen_special_numbers(current_number=num_str, divisor=next_divisor)  # type: ignore[arg-type]
        else:
            for next_digit in (d for d in "0123456789" if d not in current_number):
                next_num: str = next_digit + current_number
                if int(next_num[:3]) % divisor != 0:
                    continue
                if next_divisor is None:
                    # Chain exhausted: prepend the single unused digit as d1 (which carries no constraint).
                    yield int(next((d for d in "0123456789" if d not in next_num)) + next_num)
                else:
                    yield from gen_special_numbers(current_number=next_num, divisor=next_divisor)

    if runner.show:
        result: int = 0
        for num in gen_special_numbers():
            result += num
            print(num)
        return str(result)
    return str(sum((num for num in gen_special_numbers())))


if __name__ == "__main__":
    raise SystemExit(solve())
