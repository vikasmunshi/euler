#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 79: Passcode Derivation.

  Problem Statement:
    A common security method used for online banking is to ask the user for three
    random characters from a passcode. For example, if the passcode was 531278,
    they may ask for the 2nd, 3rd, and 5th characters; the expected reply would
    be: 317.

    The text file, keylog.txt, contains fifty successful login attempts.

    Given that the three characters are always asked for in order, analyse the
    file so as to determine the shortest possible secret passcode of unknown
    length.

  Solution Approach:
    To solve this problem, first consider each login attempt as a sequence that
    imposes ordering constraints on the digits of the secret passcode. Each three-
    character sequence indicates that the first character appears before the
    second, and the second appears before the third in the passcode.

    Collectively, all these sequences define a partial ordering on the digits. The
    task is to find the shortest passcode that respects all these ordering
    constraints. An efficient approach is to construct a directed graph where
    nodes represent digits and edges represent precedence.

    Then, perform a topological sort of the graph to obtain a linear order that
    satisfies all constraints, yielding the shortest passcode that matches all
    attempts. Ensuring the graph accurately captures the constraints from the
    login attempts is essential to obtain the correct passcode.

  Test Cases:
    main:
      asked_characters=3,
      file_url=https://projecteuler.net/resources/documents/0079_keylog.txt,
      answer=73162890.


  Answer: 73162890
  URL: https://projecteuler.net/problem=79
"""
from __future__ import annotations

from typing import Dict, Set, Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.setup.cached_requests import get_text_file


@register_solution(euler_problem=79, test_case_category=TestCaseCategory.EXTENDED)
def passcode_derivation(*, asked_characters: int, file_url: str) -> int:
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
    raise SystemExit(evaluate(euler_problem=79, time_out_in_seconds=300, mode='evaluate'))
