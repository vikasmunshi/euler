#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 74: Digit Factorial Chains [Level 2]. """
from __future__ import annotations

from solver.runners import runner

Chains = dict[int, list[int]]
digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    """Successor under the digit-factorial map: sum of factorials of n's decimal digits."""
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def add_chains(chains: Chains, number: int) -> bool:
    """Walk from number caching the full tail list for each new node; return False if already cached."""
    if number in chains:
        return False
    num: int = number
    current_chain: list[int] = []
    visited: set[int] = set()
    while num not in visited:
        visited.add(num)
        if num in chains:
            current_chain.extend(chains[num])
            break
        current_chain.append(num)
        num = sum_of_digit_factorials(num)
    loop_start: int = len(current_chain) - len(visited) if num in visited else -1
    for i, val in enumerate(current_chain):
        if val not in chains:
            chains[val] = current_chain[i:] if i >= loop_start else current_chain[i:]
    return True


def count_chains_with_max_length_digit_factorial(max_num: int) -> tuple[int, int]:
    """Cache every chain, then report the maximum chain length and how many chains attain it."""
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    chain_lengths = [len(c) for c in chains.values()]
    max_chain_length = max(chain_lengths)
    max_chain_length_count = chain_lengths.count(max_chain_length)
    return (max_chain_length, max_chain_length_count)


@runner.main
def solve(*args: str) -> str:
    """Memoize the digit-factorial functional graph storing each node's full tail list, splicing
    cached tails onto the walk; count chains of maximal length. Amortised O(1) per start, but the
    per-node list slices make it slower than the length-only variant. Overall O(max_num)."""
    max_num = runner.parse_int(args[0])

    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num)
    if runner.show:
        print(f"max_num={max_num!r} "
              f"max_chain_length={max_chain_length!r} "
              f"max_chain_length_count={max_chain_length_count!r}")
    return str(max_chain_length_count)


if __name__ == "__main__":
    raise SystemExit(solve())
