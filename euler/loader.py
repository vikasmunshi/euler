#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem retriever for Project Euler.

from euler.logger import logger
This module provides functionality to retrieve Project Euler problems
from the website and store them locally as Python modules.
"""
from __future__ import annotations

import pathlib

import requests

from euler.logger import logger
from euler.template import get_module_content


def get_problem_statement(problem_number: int) -> str | None:
    """Retrieve a Project Euler problem from the website.

    Args:
        problem_number: The number of the Project Euler problem to retrieve

    Returns:
        The problem content as a string, or None if retrieval failed
    """

    url: str = f'https://projecteuler.net/minimal={problem_number}'
    logger.info({'action': 'retrieve_problem', 'problem_number': problem_number, 'url': url})

    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        if problem_content := response.text:
            cl: int = len(problem_content)
            logger.info({'action': 'problem_retrieved', 'problem_number': problem_number, 'content_length': cl})
            return problem_content
        else:
            logger.warning({'action': 'problem_empty', 'problem_number': problem_number})
            return None

    except requests.exceptions.RequestException as e:
        logger.error({'action': 'problem_retrieval_error', 'problem_number': problem_number, 'error': str(e)})
        return None


def get_problem_module(problem_number: int) -> pathlib.Path | None:
    """Store a Project Euler problem locally.

    Args:
        problem_number: The number of the Project Euler problem to retrieve

    Returns:
        Path to the created or existing problem solution file
    """

    # Create subfolder structure based on first 4 digits
    problem_prefix = f'{problem_number:06d}'[:4]
    solutions_dir = pathlib.Path(__file__).parent / 'solutions'
    subfolder = solutions_dir / problem_prefix

    # Ensure the subfolder exists
    subfolder.mkdir(parents=True, exist_ok=True)

    # Generate the path for this problem
    local_path: pathlib.Path | None = subfolder / f'problem_{problem_number:06d}.py'

    # Only create the file if it doesn't already exist
    if not local_path.exists():
        if problem_content := get_problem_statement(problem_number):
            module_str: str = get_module_content(problem_number=problem_number, problem_content=problem_content)
            local_path.write_text(module_str)
        else:
            local_path = None

    return local_path


def get_problem_modules(start_number: int, end_number: int) -> list[pathlib.Path]:
    return [get_problem_module(problem_number=i) for i in range(start_number, end_number)]
