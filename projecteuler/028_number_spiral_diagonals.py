#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=28
Starting with the number 1 and moving to the right in a clockwise direction a 5 by 5 spiral is formed as follows:

21 22 23 24 25
20  7  8  9 10
19  6  1  2 11
18  5  4  3 12
17 16 15 14 13

It can be verified that the sum of the numbers on the diagonals is 101.

What is the sum of the numbers on the diagonals in a 1001 by 1001 spiral formed in the same way?
Answer: 669171001
"""


def number_spiral_with_diagonal_sum(size: int) -> int:
    x, y, coordinate_map = 0, 0, {(0, 0): 1}
    for number in range(2, size ** 2 + 1):
        free_adjacent_coords = (c for c in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)) if c not in coordinate_map)
        x, y = min(((c[0] ** 2 + c[1] ** 2, c) for c in free_adjacent_coords), key=lambda c: c[0])[1]
        coordinate_map[(x, y)] = number
    diagonal_sum = sum(n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1])
    return diagonal_sum


def number_spiral_diagonal_sum(size: int) -> int:
    return (size * (size * (4 * size + 3) + 8) - 9) // 6


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_compare((number_spiral_diagonal_sum, number_spiral_with_diagonal_sum),
                                      answers={5: 101, 1001: 669171001})
