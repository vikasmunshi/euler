#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0046/p0046.py
  func: solve_goldbachs_other_conjecture_p0046_s0
"""

from __future__ import annotations

from typing import Dict, List, Set


def solve() -> int:
    primes: Set[int] = set()
    known_composites: Dict[int, List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            primes.add(current_number)
            known_composites[current_number**2] = [current_number]
        else:
            if current_number % 2 != 0:
                if not any((((current_number - p) / 2) ** 0.5 % 1 == 0 for p in primes if current_number > p != 2)):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
