#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Module for AI-powered features."""
from __future__ import annotations

from typing import Literal

from solver.ai.code import generate_c_code, generate_py_code
from solver.ai.docs import generate_notes, generate_test_cases
from solver.ai.models import Model


def make(target: Literal['c', 'py', 'notes', 'test_cases'], model: Model | None = None, force: bool = False) -> None:
    """Generate AI-based content for the specified target.

    Args:
        target: The type of content to generate ('c' for code, 'notes' for documentation, 'test_cases' for test cases).
        model: The AI model to use for generation.
        force: Whether to force the generation even if the target already exists.
    """
    # Default models for each target
    default_models = {
        'c': Model.CLAUDE_OPUS_4_6,
        'py': Model.CLAUDE_OPUS_4_6,
        'notes': Model.CLAUDE_SONNET_4_6,
        'test_cases': Model.CLAUDE_HAIKU_4_5,
    }

    # Generator functions for each target
    generators = {
        'c': generate_c_code,
        'py': generate_py_code,
        'notes': generate_notes,
        'test_cases': generate_test_cases,
    }

    # Call the appropriate generator with the model (or default)
    generators[target](model=model or default_models[target], force=force)


__all__ = ('make',)
