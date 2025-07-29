#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 79: passcode_derivation

Problem Statement:
  A common security method used for online banking is to ask the user for three
  random characters from a passcode. For example, if the passcode was 531278, they
  may ask for the 2nd, 3rd, and 5th characters; the expected reply would be: 317.
  The text file, keylog.txt, contains fifty successful login attempts. Given that
  the three characters are always asked for in order, analyse the file so as to
  determine the shortest possible secret passcode of unknown length.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=79
Answer: None
"""
from __future__ import annotations

from typing import Dict, Set, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase
from euler.setup.cached_requests import get_text_file

test_cases: list[TestCase] = [
    TestCase(
        answer=73162890,
        is_main_case=False,
        kwargs={'asked_characters': 3, 'file_url': 'https://projecteuler.net/resources/documents/0079_keylog.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #79
@register_solution(problem_number=79, test_cases=test_cases)
def passcode_derivation(*, asked_characters: int, file_url: str) -> int:
    """Find the shortest possible passcode that satisfies all login attempts.

    This function implements a graph-based approach to determine the shortest possible
    passcode based on partial ordering information from login attempts. It builds a
    directed graph representing the ordering constraints between digits and performs
    a topological sort to find a valid total ordering.

    Args:
        file_url: URL to the file containing login attempt data. Each line of the file
                  should contain a sequence of digits representing a successful login attempt.
        asked_characters: Number of characters in each login attempt (typically 3 for this problem).
                         These characters are assumed to appear in the same order in the passcode.

    Returns:
        The shortest possible passcode as an integer that satisfies all ordering constraints.

    Raises:
        ValueError: If a cyclic dependency is detected in the ordering constraints,
                   indicating that no valid passcode exists.

    Example:
        >>> passcode_derivation(file_url='keylog.txt', asked_characters=3)
        73162890
    """
    # Create indices for processing consecutive character pairs
    # For 3-digit login attempts, this creates (0, 1) to process relationships between positions 0->1 and 1->2
    char_index: Tuple[int, ...] = tuple(range(asked_characters - 1))

    # Fetch the login attempt data from the provided URL
    content: str = get_text_file(file_url)

    # Create a set of unique login attempts to eliminate duplicates
    values: Set[str] = set(content.splitlines(keepends=False))

    # Initialize our directed graph as a dictionary where:
    # - Keys are individual digits appearing in the login attempts
    # - Values are sets of digits that must come after the key digit in the passcode
    successor_graph: Dict[str, Set[str]] = {char: set() for val in values for char in val}

    # Build the directed graph by analyzing each login attempt
    # For each login attempt like "123", we add the constraints: 1→2 and 2→3
    for val in values:
        for i in char_index:  # (0, 1) for 3 characters
            successor_graph[val[i]].add(val[i + 1])
    # Initialize an empty passcode that we'll build incrementally
    passcode: str = ''

    # Implement topological sort to find a valid ordering of digits
    # Continue until we've processed all digits in the graph
    while successor_graph:
        # Find a digit that doesn't need to come before any other digit (has no successors)
        # This digit can safely be placed at the end of our current partial passcode
        for char, after in successor_graph.items():
            if not after:  # This digit has no successors, so it can be processed now
                # Add this digit to the beginning of our passcode
                # We build from right to left because digits with no successors should be at the end
                passcode = char + passcode
                break
        else:
            # If no digit with empty successor set is found, we have a cycle in the graph
            # This means contradictory constraints that cannot be satisfied
            raise ValueError('No successor found - possible circular dependency in the constraints')

        # Remove the processed digit from the graph since it's now part of our passcode
        del successor_graph[char]

        # Update all successor sets to remove the processed digit
        # This effectively removes all edges pointing to the digit we just processed
        for after in successor_graph.values():
            if char in after:
                after.remove(char)
    # Convert the final passcode string to an integer and return it.
    # The resulting passcode is guaranteed to be the shortest possible one that satisfies all constraints
    # because each digit appears exactly once and in an order that respects all login attempt constraints
    return int(passcode)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(79))
