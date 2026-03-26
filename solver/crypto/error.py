#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

__all__ = ['error_handler']

P = ParamSpec('P')
T = TypeVar('T')


def error_handler(operation: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to convert exceptions in crypto functions to RuntimeError."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as err:
                print(f'{operation=}, {func.__name__=}, {args=}, {kwargs=}')
                print(f'Error: {err}')
                raise RuntimeError(f'Error {err}') from err

        return wrapper

    return decorator
