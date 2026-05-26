#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Module for AI-powered features."""
from __future__ import annotations

from typing import Literal

from solver.ai.code import generate_c_code, generate_py_code
from solver.ai.docs import generate_notes, generate_test_cases
from solver.ai.models import Model, get_accumulated_charges
from solver.config import config
from solver.shell import console, register


@register(name='make',
          help='Generate AI-based content for the specified target.',
          usage='make <target=c|py|notes|test-cases> [force=false] [major=false] [model=Model|None]', )
def make(target: Literal['c', 'py', 'notes', 'test-cases'], *,
         force: bool = False,
         major: bool = False,
         model: Model | None = None,
         ) -> Literal['ok', 'nok']:
    """Generate AI-based content for the specified target.

    Args:
        target: The type of content to generate ('c' or 'py' for code, 'notes' for documentation,
                'test-cases' for test cases).
        major:  Whether this is after a major change (e.g. template or instruction change).
        force:  Whether to force generation even if the target already exists.
        model:  The AI model to use for generation; defaults to the per-target default.
    """
    # Default models for each target
    default_models = {
        'c': Model.CLAUDE_OPUS_4_6,
        'py': Model.CLAUDE_OPUS_4_6,
        'notes': Model.CLAUDE_SONNET_4_6,
        'test-cases': Model.CLAUDE_HAIKU_4_5,
    }

    # Generator functions for each target
    generators = {
        'c': generate_c_code,
        'py': generate_py_code,
        'notes': generate_notes,
        'test-cases': generate_test_cases,
    }

    # Call the appropriate generator with the model (or default)
    charges_pre: float = get_accumulated_charges()
    result = generators[target](model=model or default_models[target], force=force, major=major)
    charges_post: float = get_accumulated_charges()
    charges_usd: float = charges_post - charges_pre
    console.print(f'${charges_usd:.4f} (€{charges_usd * config.usd_to_eur:.4f} at {config.usd_to_eur:.2f} $/€)')
    return 'nok' if result is False else 'ok'


__all__ = ('make',)
