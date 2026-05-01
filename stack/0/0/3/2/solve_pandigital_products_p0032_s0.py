#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0032/p0032.py
  func: solve_pandigital_products_p0032_s0
"""

from __future__ import annotations

from itertools import permutations

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
                for a in permutations(nine_digits, a_len)
                for b in permutations((d for d in nine_digits if d not in a), b_len)
                if is_nine_pandigital(
                    (a_str := "".join(a)) + (b_str := "".join(b)) + str((c := (int(a_str) * int(b_str))))
                )
            )
        )
    )


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
