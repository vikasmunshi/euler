#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Decorator to conditionally disable functions based on environment variables. """
from __future__ import annotations

from functools import wraps
from os import getenv
from sys import argv
from typing import Callable


def disabled[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to conditionally disable a function based on an environment variable.

    This decorator checks if the environment variable 'disabled' is set to 'false'
    and allows the execution of the decorated function only when the condition is met.
    If the condition is not met, it raises a NotImplementedError indicating that the
    function is disabled.
    """
    if getenv('disabled') == 'false' or 'disabled=false' in argv[1:]:
        return func

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        _ = (args, kwargs)
        raise NotImplementedError(f'{func.__name__} is disabled; use disabled=false to enable')

    return wrapper


__all__ = (
    'disabled',
)
