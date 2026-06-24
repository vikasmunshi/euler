#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 32: Pandigital Products [Level 2]. """
from __future__ import annotations

import itertools

from solver.runners import runner

nine_digits: tuple[str, ...] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
set_nine_digits: set[str] = set(nine_digits)


def is_nine_pandigital(n: int | str) -> bool:
    """True iff the decimal string is exactly 9 chars and uses each of 1-9 once."""
    return len(str(n)) == 9 and set(str(n)) == set_nine_digits


@runner.main
def solve(*args: str) -> str:
    """Enumerate only the (1,4) and (2,3) operand digit-length splits - the sole splits whose
    operand and product lengths can sum to 9, since a*b has len(a)+len(b) or len(a)+len(b)-1 digits -
    drawing b's digits from those a leaves unused, then sum distinct pandigital products via a set; O(1)."""
    return str(sum(
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
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
