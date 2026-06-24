#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 83: Path Sum: Four Ways [Level 4]. """
from __future__ import annotations

from solver.runners import runner

default: str = (
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n"
)


def path_sum_four_ways(content: str) -> int:
    """Minimal four-directional path sum via Dijkstra with a linear minimum scan; O(V^2) = O(N^4).

    Four-directional movement creates cycles, ruling out single-pass DP; non-negative cell weights
    make Dijkstra exact. Edge weight is the destination cell's value, and the scan stops once the
    bottom-right target is finalised. Distances/unvisited are keyed on (row, col) tuples.
    """
    matrix: list[list[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
    size = len(matrix)
    node_weights = {(row, col): matrix[row][col] for row in range(size) for col in range(size)}
    infinity = sum(node_weights.values()) + 1
    unvisited = {(row, col) for row in range(size) for col in range(size)}
    distances = {(row, col): infinity for row in range(size) for col in range(size)}
    distances[0, 0] = matrix[0][0]
    target = (size - 1, size - 1)
    while target in unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        current_row, current_col = current
        up = (current_row - 1, current_col)
        down = (current_row + 1, current_col)
        left = (current_row, current_col - 1)
        right = (current_row, current_col + 1)
        for neighbor in [up, down, left, right]:
            neighbor_row, neighbor_col = neighbor
            if 0 <= neighbor_row < size and 0 <= neighbor_col < size and (neighbor in unvisited):
                new_distance = distances[current] + node_weights[neighbor]
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
        unvisited.remove(current)
    return distances[target]


@runner.main
def solve(*args: str) -> str:
    """Load the matrix (file URL or built-in 5x5 default) and return the minimal path sum."""
    file_url = args[0]

    content: str = runner.get_text_file(file_url) if file_url else default
    return str(path_sum_four_ways(content))


if __name__ == "__main__":
    raise SystemExit(solve())
