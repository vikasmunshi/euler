#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem retriever for Project Euler.
This module provides functionality to retrieve Project Euler problems from the website and store them locally as
Python modules.
"""
from __future__ import annotations

import pathlib

import requests

from euler.logger import logger
from euler.template import get_module_content


def get_problem_statement(problem_number: int) -> str | None:
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


def problem_prefix(problem_number: int) -> str:
    # Create subfolder structure based on first 4 digits
    return f'set_{problem_number:06d}'[:8]


def get_module_path(problem_number: int) -> pathlib.Path:
    """Store a Project Euler problem locally."""
    solutions_dir = pathlib.Path(__file__).parent / 'solutions'
    # Create empty __init__.py to make the solutions dir a proper Python package
    (solutions_dir / '__init__.py').touch(exist_ok=True)
    # Create subfolder structure based on first 4 digits
    subfolder = solutions_dir / problem_prefix(problem_number)
    # Ensure the subfolder exists
    subfolder.mkdir(parents=True, exist_ok=True)
    # Create empty __init__.py to make the subfolder a proper Python package
    (subfolder / '__init__.py').touch(exist_ok=True)
    # Generate the path for this problem
    local_path: pathlib.Path = subfolder / f'problem_{problem_number:06d}.py'
    return local_path


def module_name(problem_number: int) -> str:
    return f'euler.solutions.{problem_prefix(problem_number)}.problem_{problem_number:06d}'


def load_problem_module(problem_number: int) -> bool | None:
    # Generate the path for this problem
    local_path: pathlib.Path = get_module_path(problem_number=problem_number)
    # Only create the file if it doesn't already exist
    if not local_path.exists():
        if problem_content := get_problem_statement(problem_number):
            module_str: str = get_module_content(problem_number=problem_number, problem_content=problem_content)
            local_path.write_text(module_str)
            return True
        return None
    return False


def load_problem_modules(start_number: int, end_number: int) -> int:
    modules = [load_problem_module(problem_number=i) for i in range(start_number, end_number + 1)]
    total_modules = (end_number - start_number + 1)
    num_new_modules = modules.count(True)
    num_existing_modules = modules.count(False)
    print(f'Loaded {num_new_modules}/{total_modules} new solution modules; ({num_existing_modules} existing).')
    return total_modules - (num_new_modules + num_existing_modules)
