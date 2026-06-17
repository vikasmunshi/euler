#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 46: Goldbach's Other Conjecture [Level 1]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Enumerate via an incremental sieve; for each odd composite test n = p + 2k^2 over the known
    primes, returning the first that fails. Per-candidate cost O(pi(n)), so O(N^2 / ln N) overall."""
    primes: set[int] = set()
    known_composites: dict[int, list[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            primes.add(current_number)
            known_composites[current_number**2] = [current_number]
        else:
            if current_number % 2 != 0:
                if not any((((current_number - p) / 2) ** 0.5 % 1 == 0 for p in primes if current_number > p != 2)):
                    return str(current_number)
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


if __name__ == "__main__":
    raise SystemExit(solve())
