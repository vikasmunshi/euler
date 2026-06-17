#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 92: Square Digit Chains [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def terminates_in_89(n: int) -> bool:
    """Return True if the square-digit-sum chain from n reaches the 89-cycle rather than 1."""
    while n != 1 and n != 89:
        n, t = (0, n)
        while t:
            n, t = (n + (t % 10) ** 2, t // 10)
    return n == 89


@runner.main
def solve(*args: str) -> str:
    """Count d-digit values reaching 89 by convolving the per-digit square distribution; O(d^2 * 81).

    The chain depends only on the digit-square-sum, so a[s] counts strings with sum s, grown one
    digit at a time, and only the <= 81*d distinct sums need classifying via terminates_in_89.
    """
    power_of_10 = runner.parse_int(args[0])

    a, sq, is89 = ([1], [x**2 for x in range(1, 10)], [False])
    results: dict[int, int] = {}
    for n in range(1, power_of_10 + 1):
        b, a = (a, a + [0] * 81)
        is89 += map(terminates_in_89, range(len(b), len(a)))
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v
        results[n] = sum((a[i] for i in range(len(a)) if is89[i]))
    if runner.show:
        print(f"Results for power_of_10={power_of_10}: {results}")
    return str(results[power_of_10])


if __name__ == "__main__":
    raise SystemExit(solve())
