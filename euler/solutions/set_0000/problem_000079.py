# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 79: Passcode Derivation

Problem Statement:
A common security method used for online banking is to ask the user for three random characters from a passcode.
For example, if the passcode was 531278, they may ask for the 2nd, 3rd, and 5th characters;
the expected reply would be: 317.

The text file, keylog.txt, contains fifty successful login attempts.

Given that the three characters are always asked for in order, analyse the file so as to determine the
shortest possible secret passcode of unknown length.

Solution Approach:
1. Treat this as a graph problem where each digit is a node, and ordering constraints form directed edges
2. For each login attempt with digits (a, b, c), we know a comes before b and b comes before c in the passcode
3. Build a directed graph where an edge from digit X to digit Y means X must appear before Y
4. Create a "successor graph" where each digit maps to a set of digits that must come after it
5. Perform a topological sort on this graph to find a valid ordering of all digits:
   - Find digits with no successors (these should be at the end of the passcode)
   - Add them to our result (building from right to left)
   - Remove them from the graph and update all relationships
   - Repeat until all digits are processed
6. This gives the shortest possible passcode because each digit appears exactly once and
   in an order that satisfies all constraints from the login attempts

Time Complexity: O(n²) where n is the number of unique digits
Space Complexity: O(n) for storing the graph

Test Cases:
- Using the provided keylog.txt file with 50 login attempts, we get the answer: 73162890

URL: https://projecteuler.net/problem=79
Answer: 73162890
"""
from typing import Dict, Set, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=79)
problem_number: int = 79

# Define the test cases for validating the solution
# This test case uses the official keylog.txt file from Project Euler
# which contains 50 successful login attempts, each with 3 digits
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0079_keylog.txt',
                        'asked_characters': 3},  # Each login attempt has 3 characters
                answer=73162890, ),  # The expected shortest passcode
]


# Example of how the algorithm works with a small sample:
# If login attempts are: "319", "680", "180", "690", the successor graph would be:
# {'3': {'1'}, '1': {'9'}, '9': set(), '6': {'8'}, '8': {'0'}, '0': set()}
#
# Topological sort steps:
# 1. Find digits with no successors: '9' and '0'
# 2. Add '9' to passcode (arbitrary choice), remove '9' from graph
# 3. Find digits with no successors: '0'
# 4. Add '0' to passcode, remove '0' from graph
# 5. Find digits with no successors: '1' and '8'
# 6. Add '8' to passcode, remove '8' from graph
# 7. Find digits with no successors: '1'
# 8. Add '1' to passcode, remove '1' from graph
# 9. Find digits with no successors: '3' and '6'
# 10. Add '6' to passcode, remove '6' from graph
# 11. Find digits with no successors: '3'
# 12. Add '3' to passcode, remove '3' from graph
# Final passcode: "361890" (reading from left to right)


# Register this function as a solution for problem #79 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def find_shortest_passcode(*, file_url: str, asked_characters: int) -> int:
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
        >>> find_shortest_passcode(file_url='keylog.txt', asked_characters=3)
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
    raise SystemExit(evaluate_solutions(problem_number))
