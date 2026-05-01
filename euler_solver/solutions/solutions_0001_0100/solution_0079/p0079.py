#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 79: Passcode Derivation.

Problem Statement:
    A common security method used for online banking is to ask the user for three random
    characters from a passcode. For example, if the passcode was 531278, they may ask for
    the 2nd, 3rd, and 5th characters; the expected reply would be: 317.

    The text file, keylog.txt, contains fifty successful login attempts.

    Given that the three characters are always asked for in order, analyse the file so as
    to determine the shortest possible secret passcode of unknown length.

Solution Approach:
    Use graph theory or topological sorting. Model the login attempts as ordering
    constraints between characters. Build a directed graph representing character order.
    Perform a topological sort to find the shortest passcode consistent with all attempts.
    Efficient approach involves processing 50 fixed-length triples and sorting partial orders,
    complexity roughly O(V+E) where V is digits involved and E edges between them.

Answer: 73162890
URL: https://projecteuler.net/problem=79
"""
from __future__ import annotations

from typing import Any, Dict, Set, Tuple

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 79
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'asked_characters': 3,
                                   'file_url': 'https://projecteuler.net/resources/documents/0079_keylog.txt'},
     'answer': 73162890},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_passcode_derivation_p0079_s0(*, asked_characters: int, file_url: str) -> int:
    char_index: Tuple[int, ...] = tuple(range(asked_characters - 1))
    content: str = get_text_file(file_url)
    values: Set[str] = set(content.splitlines(keepends=False))
    successor_graph: Dict[str, Set[str]] = {char: set() for val in values for char in val}
    for val in values:
        for i in char_index:
            successor_graph[val[i]].add(val[i + 1])
    passcode: str = ''
    while successor_graph:
        for char, after in successor_graph.items():
            if not after:
                passcode = char + passcode
                break
        else:
            raise ValueError('No successor found - possible circular dependency in the constraints')
        del successor_graph[char]
        for after in successor_graph.values():
            if char in after:
                after.remove(char)
    return int(passcode)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
