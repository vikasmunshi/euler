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


@register(requires='contributor', help_text='Generate specified target using Claude API.')
def claude_api(problem: Problem,
               target: Literal['c', 'py', 'doc', 'notes', 'tags', 'test-cases'], *,
               force: bool = False,
               major: bool = False,
               model: Model | None = None,
               ) -> int:
    """Generate AI-based content for the specified target.

    Args:
        problem: The `problem` to generate for; defaults to the current problem.
        target: The type of content to generate ('c' or 'py' for code, 'doc' to refresh in-source
                docs, 'notes' for documentation, 'tags' for tags.json, 'test-cases' for test cases).
        major:  Whether this is after a major change (e.g. template or instruction change).
        force:  Whether to force generation even if the target already exists.
        model:  The AI model to use for generation; defaults to Opus for code, docs and notes, Sonnet for test cases.

    Prints the USD/EUR cost of the call and returns non-zero if the generator reports failure.
    """
    if (generators := _get_generate_funcs()) is None:
        return ExitCodes.EXIT_ERROR

    # Default models for each target
    default_models = {
        'c': Model.CLAUDE_OPUS_4_8,
        'py': Model.CLAUDE_OPUS_4_8,
        'doc': Model.CLAUDE_OPUS_4_8,
        'notes': Model.CLAUDE_OPUS_4_8,
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
