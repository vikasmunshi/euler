# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from euler.setup.cached_requests import get_text_file


def load_matrix(file_url: str | None) -> List[List[int]]:
    if file_url:
        content: str = get_text_file(file_url)
        matrix: List[List[int]] = [[int(n) for n in line.split(',')] for line in content.splitlines(keepends=False)]
    else:
        matrix = [[131, 673, 234, 103, 18], [201, 96, 342, 965, 150], [630, 803, 746, 422, 111],
                  [537, 699, 497, 121, 956], [805, 732, 524, 37, 331]]
    return matrix
