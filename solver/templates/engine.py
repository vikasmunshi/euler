#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Template rendering: the Templates enum and string.Template engine with shared prompt/solution vars."""
from __future__ import annotations

__all__ = ['Templates', 'filled_template', 'get_template']

from enum import StrEnum
from functools import lru_cache
from string import Template
from typing import NamedTuple

from solver.config import config


class Templates(StrEnum):
    NEW_C = 'new.c'
    NEW_PY = 'new.py'
    PROMPT_C = 'prompt_c.txt'
    PROMPT_DOC = 'prompt_doc.txt'
    PROMPT_PY = 'prompt_py.txt'
    PROMPT_NOTES = 'prompt_notes.txt'
    PROMPT_TAGS = 'prompt_tags.txt'
    PROMPT_TAGS_DOMAIN = 'prompt_tags_domain.txt'
    PROMPT_TEST_CASES = 'prompt_test_cases.txt'


#: Shared substitutions injected into every filled template, so common prose (file-naming
#: conventions, house typography rules, etc.) lives in one place instead of being duplicated
#: across prompt files. Keys must not collide with Facts fields.
_COMMON_VARS: dict[str, str] = {
    'file_naming': (
        'Solutions may be written in Python or C. Each filename encodes the problem number and '
        'solution index (e.g. p0001_s0.py, p0001_s0.c). Python and C files with the same index '
        'implement the same algorithm in different languages; files with different indices use '
        'different algorithms.\n'
        'In benchmark/results tables the naming is:\n'
        '- Python solutions: `p000N_sM.py` (e.g. `p0001_s0.py`)\n'
        '- C solutions: `p000N_sM_c` (e.g. `p0001_s0_c`) - note the `_c` suffix and no extension.'
    ),
    'house_style': (
        'Use a hyphen-minus (-) instead of an em dash (—) throughout. '
        'Use straight ASCII quotes, not typographic ones.'
    ),
}

#: Convention docs that are the single source of truth for each topic. Each markdown file lives
#: under `docs/` (the `convention_*.md` guides) and is injected here, as a $<var> substitution,
#: into whichever prompts are relevant — so the prose lives in exactly one place. Keys must not
#: collide with _COMMON_VARS keys or Facts fields.
_CONVENTION_DOC_FILES: dict[str, str] = {
    'python_solution_conventions': 'convention_python_solution.md',
    'c_translation_conventions': 'convention_c_translation.md',
    'source_documentation_conventions': 'convention_source_documentation.md',
    'documentation_conventions': 'convention_documentation.md',
    'tag_conventions': 'convention_tags.md',
    'test_case_conventions': 'convention_test_cases.md',
}


@lru_cache(maxsize=None)
def _convention_docs() -> dict[str, str]:
    """Read the shared convention-doc markdown files, keyed by their template variable name."""
    return {var: config.docs_dir.joinpath(name).read_text().strip()
            for var, name in _CONVENTION_DOC_FILES.items()}


def filled_template(filename: Templates, /, *, facts: NamedTuple, **kwargs: str) -> str:
    """Return a template filled with the given keyword arguments and shared boilerplate vars.

    The shared convention docs (injected as $<var>) and `_COMMON_VARS` are made available to every
    template; `str.Template.substitute` simply ignores the ones a given template does not reference.
    """
    return get_template(filename).substitute(
        **_COMMON_VARS, **_convention_docs(), **facts._asdict(), **kwargs)


@lru_cache(maxsize=None)
def get_template(filename: Templates) -> Template:
    """Retrieve a template by filename from the 'templates' directory."""
    return Template(config.templates_dir.joinpath(filename).read_text())
