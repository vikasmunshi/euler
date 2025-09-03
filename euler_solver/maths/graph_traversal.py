#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph traversal helpers

Utilities for solving classic path problems on small graphs used in Project
Euler problems. Currently provides an efficient solver for the maximum path sum
in a triangular grid using bottom-up dynamic programming. The implementation
operates on a deep-copied structure so the caller’s input is never mutated.

Public API
- max_path_sum_triangle(triangle): compute the maximum path sum from top to
  bottom in a triangle of integers.

Example
>>> from euler_solver.maths.graph_traversal import max_path_sum_triangle
>>> tri = [
...     [3],
...     [7, 4],
...     [2, 4, 6],
...     [8, 5, 9, 3],
... ]
>>> max_path_sum_triangle(tri)
23
"""
from __future__ import annotations

from copy import deepcopy
from typing import List


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    """
    Compute the maximum path sum in a triangle of integers.

    Starting at the top of the triangle, at each step you may move to one of the
    two adjacent numbers in the row below. This function returns the maximum
    possible sum along such a path. The input is deep-copied to avoid mutation.

    Args:
        triangle (List[List[int]]): Triangle represented as a list of rows, where
            row i has i+1 non-negative integers.

    Returns:
        int: The maximum sum achievable from top to bottom.

    Notes:
        - Complexity: O(n^2) time and O(n^2) space in the size of the triangle.
        - Non-mutating: operates on a deepcopy of the provided triangle.
    """
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


def get_minimum_spanning_tree_for_weighted_graph(graph: list[list[int]]) -> list[list[int]]:
    """
    Compute the minimum spanning tree for a weighted undirected graph using Kruskal's algorithm.

    Args:
        graph (List[List[int]]): Adjacency matrix representation of weighted graph where
            graph[i][j] represents the weight of edge between vertices i and j.
            A weight of 0 indicates no edge.

    Returns:
        List[List[int]]: Adjacency matrix of the minimum spanning tree with same
            dimensions as input graph.

    Notes:
        - Complexity: O(E log E) where E is the number of edges
        - Non-mutating: returns a new adjacency matrix
    """
    n = len(graph)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] != 0:
                edges.append((graph[i][j], i, j))

    edges.sort()  # Sort edges by weight
    parent = list(range(n))

    def find(x: int) -> int:
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    mst = [[0] * n for _ in range(n)]
    for weight, u, v in edges:
        if find(u) != find(v):
            union(u, v)
            mst[u][v] = mst[v][u] = weight

    return mst
