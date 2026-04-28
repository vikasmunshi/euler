#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0083/p0083.py :: solve_path_sum_four_ways_p0083_s0.

Project Euler Problem 83: Path Sum: Four Ways.

Problem Statement:
    NOTE: This problem is a significantly more challenging version of Problem 81.

    In the 5 by 5 matrix below, the minimal path sum from the top left to the bottom
    right, by moving left, right, up, and down, is indicated in bold red and is equal
    to 2297.

        131   673   234   103    18
        201    96   342   965   150
        630   803   746   422   111
        537   699   497   121   956
        805   732   524    37   331

    Find the minimal path sum from the top left to the bottom right by moving left,
    right, up, and down in matrix.txt (right click and "Save Link/Target As..."), a
    31K text file containing an 80 by 80 matrix.

Solution Approach:
    Model the matrix as a weighted graph with nodes as cells and edges connecting
    adjacent cells in four directions. Use Dijkstra's algorithm or similar shortest
    path graph search techniques to find the minimal path sum efficiently. Time
    complexity roughly O(n^2 log n) for an n x n matrix, suitable for 80x80 input.

Answer: 425185
URL: https://projecteuler.net/problem=83"""
from __future__ import annotations

from pathlib import Path
from typing import List


def path_sum_four_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(',')] for line in content.splitlines(keepends=False) if line]
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


def get_text_file(url: str) -> str:
    """ Return the contents of a file from the 'resources' directory. """
    local_filename: str = 'resources' + '/' + url.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


default: str = ('131, 673, 234, 103, 18\n'
                '201, 96, 342, 965, 150\n6'
                '30, 803, 746, 422, 111\n5'
                '37, 699, 497, 121, 956\n'
                '805, 732, 524, 37, 331\n')


def solve(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_four_ways(content)


if __name__ == '__main__':
    import sys

    print(solve(file_url=str(sys.argv[1])))
