#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `claude-api` command: generate solution artifacts (code / docs / test cases) via the Claude API."""
from __future__ import annotations

__all__ = ['claude_api']

from functools import lru_cache
from typing import Literal, Protocol

from solver.ai.models import Model, get_accumulated_charges
from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register


class GeneratorFunc(Protocol):
    def __call__(self, model: Model, *,
                 problem: Problem,
                 force: bool,
                 major: bool,
                 ) -> bool | None: ...


@lru_cache(maxsize=None)
def _get_generate_funcs() -> dict[str, GeneratorFunc] | None:
    """Lazily import the claude_api function."""
    try:  # the generators pull in `anthropic`; imported on demand so the shell starts without the `ai` group
        from solver.ai.code import document_code, generate_c_code, generate_py_code
        from solver.ai.docs import generate_notes, generate_tags, generate_test_cases
    except ImportError as exc:
        console.print(f'[error]claude-api needs the [accent]ai[/accent] dependency group '
                      f'({exc.name} is not installed) — run [accent]pip install -e ".\\[ai]"[/accent].[/error]')
        return None
    return {
        'c': generate_c_code,
        'py': generate_py_code,
        'doc': document_code,
        'notes': generate_notes,
        'tags': generate_tags,
        'test-cases': generate_test_cases,
    }


@register(requires='contributor')
def claude_api(problem: Problem,
               target: Literal['c', 'py', 'doc', 'notes', 'tags', 'test-cases'], *,
               force: bool = False,
               major: bool = False,
               model: Model | None = None,
               ) -> int:
    """Generate one of a problem's solution artifacts through the Claude API.

    Dispatches to the generator for *target*, prints the USD/EUR cost of the call, and fails
    if the generator reports failure.

    Args:
        problem: [problem] The problem to generate for.
        target: What to generate: 'c' or 'py' for code, 'doc' to refresh the in-source
            documentation, 'notes' for `notes.html`, 'tags' for `tags.json`, 'test-cases'
            for test cases.
        force: Generate even when the target already exists, overwriting it. Defaults to
            False.
        major: Regenerate after a major change — a new template or changed instructions —
            rather than an incremental one. Defaults to False.
        model: The model to generate with. Defaults to None, which picks Opus for code, docs
            and notes, and Sonnet for tags and test cases.
    """
    if (generators := _get_generate_funcs()) is None:
        return ExitCodes.EXIT_ERROR

    # Default models for each target
    default_models = {
        'c': Model.CLAUDE_OPUS_5,
        'py': Model.CLAUDE_OPUS_5,
        'doc': Model.CLAUDE_OPUS_5,
        'notes': Model.CLAUDE_OPUS_5,
        'tags': Model.CLAUDE_SONNET_4_6,
        'test-cases': Model.CLAUDE_SONNET_4_6,
    }

    # Call the appropriate generator with the model (or default)
    charges_pre: float = get_accumulated_charges()
    result = generators[target](model=model or default_models[target], problem=problem, force=force, major=major)
    charges_post: float = get_accumulated_charges()
    charges_usd: float = charges_post - charges_pre
    console.print(f'${charges_usd:.4f} (€{charges_usd / config.ecb_usd_rate:.4f} at {config.ecb_usd_rate:.2f} €/$)')
    return ExitCodes.EXIT_ERROR if result is False else ExitCodes.EXIT_OK
