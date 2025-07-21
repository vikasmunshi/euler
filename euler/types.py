#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type definitions for Project Euler solutions.

This module provides type annotations for Project Euler solution functions and related structures.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProblemArgs:
    """Represents arguments for a problem solution with the expected answer.

    Attributes:
        kwargs: Keyword arguments to pass to the solution function
        answer: The expected answer for the given inputs
    """
    kwargs: Dict[str, Any] = field(default_factory=dict)
    answer: Optional[Any] = field(default=None)


ProblemArgsList = List[ProblemArgs]


class EulerError(ValueError):
    """Base class for all Euler-related errors."""
    pass
