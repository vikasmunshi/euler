#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 74: Digit Factorial Chains [Level 2]. """
from __future__ import annotations

from solver.runners import runner

digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    """Successor under the digit-factorial map: sum of factorials of n's decimal digits."""
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def find_max_length_chains_digit_factorial(max_num: int) -> tuple[int, int]:
    """Walk-and-cache memoization of chain lengths, then count those equal to the maximum."""
    chain_length_cache: dict[int, int] = {}
    graph: dict[int, int] = {}
    max_chain_length: int = 0
    max_chain_length_count: int = 0
    for start in range(2, max_num + 1):
        # Walk forward until we revisit a node in this walk (cycle) or hit a cached length.
        seen: list[int] = []
        current: int = start
        while current not in seen and current not in chain_length_cache:
            seen.append(current)
            if current not in graph:
                graph[current] = sum_of_digit_factorials(current)
            current = graph[current]
        if current in chain_length_cache:
            length = len(seen) + chain_length_cache[current]
        else:
            length = len(seen)
        # Back-propagate: seen[i] is i steps along the same chain, so its length is length - i.
        for i, num in enumerate(seen):
            chain_length_cache[num] = length - i
            graph[num] = seen[i + 1] if i + 1 < len(seen) else current
        if (chain_length := chain_length_cache[start]) > max_chain_length:
            max_chain_length = chain_length
            max_chain_length_count = 1
        elif chain_length == max_chain_length:
            max_chain_length_count += 1
    return (max_chain_length, max_chain_length_count)


@runner.main
def solve(*args: str) -> str:
    """Memoize chain lengths over the digit-factorial functional graph, back-propagating each
    walk's lengths into a cache so every start is amortised O(1); count starts hitting the
    maximum. Overall O(max_num)."""
    max_num = runner.parse_int(args[0])

    max_chain_length, max_chain_length_count = find_max_length_chains_digit_factorial(max_num)
    if runner.show:
        print(f"max_num={max_num!r} "
              f"max_chain_length={max_chain_length!r} "
              f"max_chain_length_count={max_chain_length_count!r}")
    return str(max_chain_length_count)


if __name__ == "__main__":
    raise SystemExit(solve())
