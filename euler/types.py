#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type definitions for Project Euler solutions.

This module provides type annotations for Project Euler solution functions and related structures.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union, Protocol


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

# Common solution return types
SolutionResult = Union[int, float, str, List[Any], Dict[str, Any]]


class SolutionProtocol(Protocol):
    """Protocol defining the structure of a Project Euler solution function.

    This protocol is more restrictive than the basic Solution type as it enforces
    keyword-only arguments and provides better static type checking.
    """

    def __call__(self, *, kwargs: Any) -> SolutionResult:
        """Execute the solution with the provided keyword-only arguments.

        The asterisk (*) indicates that all arguments must be passed as keywords,
        not positional arguments. This matches the pattern used in Project Euler solutions.

        Args:
            **kwargs: Keyword arguments specific to the problem (e.g., max_limit, target_sum)

        Returns:
            The solution result
        """
        ...
