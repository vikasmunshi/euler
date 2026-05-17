#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" """
from __future__ import annotations

from bs4 import BeautifulSoup

from solver.core.config import Config
from solver.core.stack import read_stack_file


def get_solution_notes_html(problem_number: int) -> str:
    """
    Extract the inner HTML of the solution notes div from the existing HTML stack file.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        The inner HTML string of the solution notes div, or an empty string if the
        file does not exist or the div is absent.
    """
    solution_notes: str = f'<p><em>{Config.default_solution_notes}</em></p>'
    try:
        html_bytes: bytes = read_stack_file(problem_number, Config.statement_filename)[0]
        soup: BeautifulSoup = BeautifulSoup(html_bytes.decode(), 'html.parser')
        if div := soup.find('div', id='solution-notes-content'):
            solution_notes = div.decode_contents().strip('\n')
    except FileNotFoundError:
        pass
    return solution_notes


__all__ = ('get_solution_notes_html',)
