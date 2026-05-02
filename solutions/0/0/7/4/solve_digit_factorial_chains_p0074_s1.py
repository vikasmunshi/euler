#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0074/p0074.py
  func: solve_digit_factorial_chains_p0074_s1
"""

from __future__ import annotations

from sys import argv


def show_solution() -> bool:
    return "--show" in argv


Chains = dict[int, list[int]]


digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result


def add_chains(chains: Chains, number: int) -> bool:
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
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    chain_lengths = [len(c) for c in chains.values()]
    max_chain_length = max(chain_lengths)
    max_chain_length_count = chain_lengths.count(max_chain_length)
    return (max_chain_length, max_chain_length_count)


def solve(*, max_num: int) -> int:
    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num)
    if show_solution():
        print(
            f"max_num={
                max_num!r} max_chain_length={
                max_chain_length!r} max_chain_length_count={
                max_chain_length_count!r}")
    return max_chain_length_count


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
