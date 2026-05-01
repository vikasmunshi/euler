#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0079/p0079.py
  func: solve_passcode_derivation_p0079_s0
"""

from __future__ import annotations

from pathlib import Path
from sys import argv
from typing import Dict, Set, Tuple


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, asked_characters: int, file_url: str) -> int:
    char_index: Tuple[int, ...] = tuple(range(asked_characters - 1))
    content: str = get_text_file(file_url)
    values: Set[str] = set(content.splitlines(keepends=False))
    successor_graph: Dict[str, Set[str]] = {char: set() for val in values for char in val}
    for val in values:
        for i in char_index:
            successor_graph[val[i]].add(val[i + 1])
    passcode: str = ""
    while successor_graph:
        for char, after in successor_graph.items():
            if not after:
                passcode = char + passcode
                break
        else:
            raise ValueError("No successor found - possible circular dependency in the constraints")
        del successor_graph[char]
        for after in successor_graph.values():
            if char in after:
                after.remove(char)
    return int(passcode)


def main() -> int:
    print(solve(asked_characters=int(argv[1]), file_url=str(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
