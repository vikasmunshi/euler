#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 95: Amicable Chains [Level 5]. """
from __future__ import annotations

from solver.runners import runner


def longest_amicable_chain(max_num: int) -> tuple[int, int]:
    """Additive sieve for proper-divisor sums, then walk the n -> s(n) functional graph; O(N log N)."""
    divisor_sum: list[int] = [0] * (max_num + 1)
    # Additive sieve: push each divisor i onto every multiple, giving s(n) for all n.
    for i in range(1, max_num // 2 + 1):
        for j in range(i * 2, max_num + 1, i):
            divisor_sum[j] += i
    smallest_member, longest_length = (0, 0)
    seen: dict[int, int] = {}
    # Walk each unclassified node's chain once; a cycle closing at i (the smallest
    # member, since i increases) yields an amicable chain. set ch gives O(1) membership.
    for i in range(1, max_num + 1):
        if i not in seen:
            ch, c, path = ({i}, divisor_sum[i], [i])
            while i <= c <= max_num and c not in ch:
                ch.add(c)
                path.append(c)
                c = divisor_sum[c]
            if c == i:
                if (len_ch := len(ch)) > longest_length:
                    longest_length, smallest_member = (len_ch, i)
                for x in path:
                    seen[x] = len_ch
    return (longest_length, smallest_member)


@runner.main
def solve(*args: str) -> str:
    """Additive sieve for s(n) plus functional-graph cycle walk; report the longest chain's min; O(N log N)."""
    max_num = runner.parse_int(args[0])

    longest_length, smallest_member = longest_amicable_chain(max_num)
    if runner.show:
        print(f"Smallest Member of longest chain of length "
              f"longest_length={longest_length!r} is smallest_member={smallest_member!r}")
    return str(smallest_member)


if __name__ == "__main__":
    raise SystemExit(solve())
