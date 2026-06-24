#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 79: Passcode Derivation [Level 2]. """
from __future__ import annotations

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Topological sort by repeated sink removal over the digit-ordering DAG; O(D^2) in distinct
    digits D. Each login's consecutive pairs give "X precedes Y" edges (stored as a successor set);
    a node with empty successor set is a sink, so prepending it builds the passcode left-to-right.
    """
    asked_characters = runner.parse_int(args[0])
    file_url = args[1]

    char_index: tuple[int, ...] = tuple(range(asked_characters - 1))
    content: str = runner.get_text_file(file_url)
    # Deduplicate logins via a set: repeated lines add no new ordering constraints.
    values: set[str] = set(content.splitlines(keepends=False))
    successor_graph: dict[str, set[str]] = {char: set() for val in values for char in val}
    for val in values:
        for i in char_index:
            successor_graph[val[i]].add(val[i + 1])
    passcode: str = ""
    while successor_graph:
        # for/else: break on finding a sink (empty successor set); else signals an unbreakable cycle.
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
    return str(int(passcode))


if __name__ == "__main__":
    raise SystemExit(solve())
