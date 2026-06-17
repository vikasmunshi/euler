#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 74: Digit Factorial Chains [Level 2]. """
from __future__ import annotations

import enum

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


def get_chain(max_num: int) -> Chains:
    """Build the full chain cache for all starts in [2, max_num] (used by the --show display)."""
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    return chains


def count_chains_with_max_length_digit_factorial(max_num: int) -> tuple[int, int]:
    """Cache every chain, then report the maximum chain length and how many chains attain it."""
    chains: Chains = {}
    for num in range(2, max_num + 1):
        add_chains(chains, num)
    chain_lengths = [len(c) for c in chains.values()]
    max_chain_length = max(chain_lengths)
    max_chain_length_count = chain_lengths.count(max_chain_length)
    return (max_chain_length, max_chain_length_count)


class ColorCodes(enum.StrEnum):
    """ANSI escape sequences for coloured terminal output; StrEnum members drop into f-strings."""
    GREEN = "\x1b[92m"
    YELLOW = "\x1b[93m"
    RED = "\x1b[91m"
    ORANGE = "\x1b[38;5;208m"
    BLUE = "\x1b[94m"
    CYAN = "\x1b[96m"
    MAGENTA = "\x1b[95m"
    WHITE = "\x1b[97m"
    BLACK = "\x1b[30m"
    GRAY = "\x1b[90m"
    BOLD = "\x1b[1m"
    UNDERLINE = "\x1b[4m"
    RESET = "\x1b[0m"


def print_chains(chains: Chains) -> None:
    """Render each chain with its cycle entry highlighted, plus aggregate statistics."""
    for start, chain in sorted(chains.items()):
        cycle: int = sum_of_digit_factorials(chain[-1])
        print(
            f"{ColorCodes.GREEN}{start}{ColorCodes.RESET} -> ",
            " -> ".join(
                (f"{ColorCodes.BLUE}{num}{ColorCodes.RESET}" if num == cycle else f"{num}" for num in chain[1:])
            ),
            f" -> {ColorCodes.BLUE}{cycle}{ColorCodes.RESET}",
        )
    max_chain_length: int = 0
    nums: list[int] = []
    for chain in chains.values():
        if len(chain) > max_chain_length:
            max_chain_length = len(chain)
        nums.extend(chain)
    unique_nums: set[int] = set(nums)
    print(f"len(chains)={len(chains)!r} "
          f"len(nums)={len(nums)!r} "
          f"len(unique_nums)={len(unique_nums)!r} "
          f"len(nums)/len(unique_nums)={len(nums) / len(unique_nums):.2f} "
          f"max_chain_length={max_chain_length!r}")


@runner.main
def solve(*args: str) -> str:
    """Same algorithm as s1 (memoize full tail lists over the digit-factorial functional graph,
    counting maximal-length chains), with optional coloured --show visualisation. Amortised O(1)
    per start, O(max_num) total."""
    max_num = runner.parse_int(args[0])

    max_chain_length, max_chain_length_count = count_chains_with_max_length_digit_factorial(max_num=max_num)
    if runner.show:
        if max_num <= 1000:
            chains: Chains = get_chain(max_num)
            print_chains(chains)
        print(f"max_num={max_num!r} "
              f"max_chain_length={max_chain_length!r} "
              f"max_chain_length_count={max_chain_length_count!r}")
    return str(max_chain_length_count)


if __name__ == "__main__":
    raise SystemExit(solve())
