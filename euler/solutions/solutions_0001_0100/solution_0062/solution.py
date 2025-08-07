#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 62: Cubic Permutations.

  Problem Statement:
    The cube, 41063625 (345 x 345 x 345), can be permuted to produce two other cubes: 56623104
    (384 x 384 x 384) and 66430125 (405 x 405 x 405). In fact, 41063625 is the smallest cube
    which has exactly three permutations of its digits which are also cube.

    Find the smallest cube for which exactly five permutations of its digits are cube.

  Solution Approach:
    To solve this problem, generate cubes of consecutive integers and sort the digits
    of each cube to form a signature that identifies permutations. Use a data structure
    like a dictionary that maps this digit signature to all cubes sharing it. Track the
    occurrences of each signature to find when exactly five cubes share the same digit
    permutation. The smallest cube with this property is the desired answer. Efficient
    checking and sorting, along with careful management of digit signatures, are key
    to solving this problem within reasonable time and memory constraints.

  Test Cases:
    preliminary:
      num_permutations=2,
      answer=125.

      num_permutations=3,
      answer=41063625.

      num_permutations=4,
      answer=1006012008.

    main:
      num_permutations=5,
      answer=127035954683.

    extended:
      num_permutations=6,
      answer=1000600120008.

      num_permutations=7,
      answer=10569784298536.

      num_permutations=8,
      answer=10314675896832.

      num_permutations=9,
      answer=13465983902671.


  Answer: 127035954683
  URL: https://projecteuler.net/problem=62
"""
from __future__ import annotations

from collections import defaultdict
from math import ceil
from typing import Dict, Set, Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


def n_digit_cubes(digit_length_n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = ceil((10 ** digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i ** 3 for i in range(start_range, stop_range)))


@register_solution(euler_problem=62, test_case_category=TestCaseCategory.EXTENDED)
def cubic_permutations(*, num_permutations: int) -> int:
    digit_length: int = 2
    while True:
        cube_numbers: Tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: Dict[str, list[int]] = defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes[''.join(sorted(str(cube_number)))].append(cube_number)
        solutions: Set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if show_solution():
                print(f'Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}')
                print(f'solutions={solutions!r}')
            return min(solutions)
        digit_length += 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=62, time_out_in_seconds=300, mode='evaluate'))
