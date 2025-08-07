#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Graph Traversal"""
from __future__ import annotations

from copy import deepcopy
from typing import List


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]
