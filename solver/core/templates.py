#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from string import Template
from typing import NamedTuple

from solver.core.config import config


class Templates(StrEnum):
    INDEX = 'index.html'
    NEW_C = 'new.c'
    NEW_PY = 'new.py'
    PROBLEM = 'problem.html'
    PROMPT_C = 'prompt_c.txt'
    PROMPT_PY = 'prompt_py.txt'
    PROMPT_NOTES = 'prompt_notes.txt'
    PROMPT_TEST_CASES = 'prompt_test_cases.txt'


def filled_template(filename: Templates, /, *, facts: NamedTuple, **kwargs: str) -> str:
    """Return a template filled with the given keyword arguments."""
    return get_template(filename).substitute(**facts._asdict(), **kwargs)


@lru_cache(maxsize=None)
def get_template(filename: Templates) -> Template:
    """Retrieve a template by filename from the 'templates' directory."""
    return Template(config.templates_dir.joinpath(filename).read_text())


__all__ = ('Templates', 'filled_template', 'get_template')
