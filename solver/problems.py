#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from typing import NamedTuple

from solver.config import problem_number_file, problems_list_url
from solver.download import download_file

__all__ = ['Problem', 'problems']


class Problem(NamedTuple):
    number: int
    title: str
    difficulty: str | None = None

    def __str__(self) -> str:
        """Return a human-readable label in the form '<number>: <title>'."""
        if self.difficulty:
            return f'{self.number}: "{self.title}" (level {self.difficulty})'
        return f'{self.number}:"{self.title}"'

    @classmethod
    def from_workspace(cls) -> Problem | None:
        """
        Read the current workspace's problem number file and return the matching Problem.

        Returns:
            The Problem for the active workspace, or None if no workspace is initialised
            or the problem number file is missing or invalid.
        """
        try:
            return cls.from_number(int(problem_number_file.read_text()))
        except (FileNotFoundError, ValueError):
            return None

    @classmethod
    def from_number(cls, problem_number: int) -> Problem | None:
        """
        Create a Problem instance from a given problem number.

        Args:
            problem_number: The problem number to create the Problem for.

        Returns:
            The Problem for the given number, or None if the number is invalid or not found.
        """
        try:
            return problems_dict[problem_number]
        except KeyError:
            return None


def _problems() -> list[Problem]:
    """
    Fetch and parse the list of all Project Euler problems.

    Returns:
        A list of Problem instances for all available problems.
        Returns an empty list if the download fails.
    """
    content: bytes | None = download_file(problems_list_url, check_last_modified=True)
    if content is None:
        print('Error: Failed to download problem list from Project Euler')
        return []
    result = []
    for line in content.strip().splitlines()[1:]:
        if not line:
            continue
        parts = line.split(b'##')
        if len(parts) >= 2:
            problem_number: int = int(parts[0].split(b'.')[0])
            title: str = parts[1].decode('utf-8').split(':', 1)[0].strip()
            result.append(Problem(problem_number, title))
    return sorted(result, key=lambda p: p.number)


problems: list[Problem] = _problems()
problems_dict: dict[int, Problem] = {p.number: p for p in problems}
