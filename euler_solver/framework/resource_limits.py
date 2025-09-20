#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Utilities Module

This module provides decorators and utilities for handling system-level exceptions
and resource limitations, particularly useful for computationally intensive
operations that might exceed Python's default recursion limits or integer conversion limits.

Features:
- Dynamically adjust recursion limits based on function arguments
- Remove integer string conversion limitations when required
"""

from functools import wraps
from inspect import Parameter, Signature, signature
from sys import getrecursionlimit, set_int_max_str_digits, setrecursionlimit
from typing import Callable, Literal, ParamSpec, TypeVar, cast

from euler_solver.framework.logger import logger

PS = ParamSpec("PS")  # ParamSpec to capture the parameter specification of the functions being decorated
RT = TypeVar("RT")  # TypeVar to represent the return type of the functions being decorated


def set_resource_limits(
        *,
        recursion_var: str | None = None,
        multiplier: int = 1,
        set_int_max_str: bool = False,
        when: Literal['always', 'on-exception'] = 'always'
) -> Callable[[Callable], Callable]:
    """
    Decorator to dynamically manage resource limits during function execution.

    This decorator helps manage system resource exceptions automatically:
    - Adjusts recursion limits dynamically based on a keyword argument
    - Removes the limit on maximum integer string conversion length if needed

    Parameters:
    -----------
    recursion_var : str, optional
        The name of the keyword argument that contains the value to be used for calculating
        the new recursion limit. Used only when recursion adjustment is needed.
    multiplier : int, optional
        A multiplier applied to the 'recursion_var' value to calculate the required recursion limit
        (default is 1). Ignored if 'recursion_var' is not provided.
    set_int_max_str : bool, optional
        If set to True, removes the system limit on maximum integer string conversion length.

    Returns:
    --------
    Callable
        A decorator function that wraps the target function.

    Example:
    --------
    >>> @set_resource_limits(recursion_var='depth', multiplier=2, set_int_max_str=True)
    >>> def recursive_function(n, depth=100):
    >>>     # If this exceeds the recursion limit, the limit will be dynamically adjusted
    >>>     return recursive_function(n-1, depth) if n > 0 else 0

    Notes:
    ------
    - The recursion limit is only adjusted when 'recursion_var' is provided.
    - Removing the integer string conversion limit should generally be used with caution.
    """

    def decorator(func: Callable[PS, RT]) -> Callable[PS, RT]:
        """Actual decorator function that wraps the provided callable."""
        if when not in ('always', 'on-exception'):
            raise TypeError(f"Invalid value for 'when': {when} in '{func.__name__}'. "
                            f"Must be one of 'always' or 'on-exception'.")
        if recursion_var is None and set_int_max_str is False:
            raise TypeError(f"At least one of 'recursion_var' or 'set_int_max_str' must be used "
                            f"in '{func.__name__}'.")
        if recursion_var:
            sig: Signature = signature(func)
            recursion_var_param = sig.parameters.get(recursion_var)
            if recursion_var_param is None or recursion_var_param.kind != Parameter.KEYWORD_ONLY:
                raise TypeError(f"'{recursion_var}' not defined as keyword only argument in '{func.__name__}'.")
            if recursion_var_param.annotation != 'int' and recursion_var_param.annotation != int:
                raise TypeError(f"'{recursion_var}' must be int in '{func.__name__}'.")

        if when == 'always':
            @wraps(func)
            def wrapper_pre_assign(*args: PS.args, **kwargs: PS.kwargs) -> RT:
                """Wrapper that assigns resources before function execution."""
                if recursion_var is not None:
                    if (current_limit := getrecursionlimit()) < (
                            required_limit := cast(int, kwargs[recursion_var]) * multiplier) * 1.1:
                        logger.info({'action': 'adjusting_recursion_limit', 'current_limit': current_limit,
                                     'revised_limit': required_limit + current_limit})
                        setrecursionlimit(required_limit + current_limit)
                if set_int_max_str:
                    logger.info({'action': 'removing_int_max_str_limit'})
                    set_int_max_str_digits(0)
                return func(*args, **kwargs)

            return wrapper_pre_assign
        else:
            @wraps(func)
            def wrapper_assign_on_exception(*args: PS.args, **kwargs: PS.kwargs) -> RT:
                """Wrapper that assigns resources on exception during function execution."""
                try:
                    return func(*args, **kwargs)
                except RecursionError as e:
                    if recursion_var is not None:
                        current_limit: int = getrecursionlimit()
                        required_limit: int = cast(int, kwargs[recursion_var]) * multiplier
                        logger.info({'action': 'adjusting_recursion_limit', 'current_limit': current_limit,
                                     'revised_limit': required_limit + current_limit})
                        setrecursionlimit(required_limit + current_limit)
                        return func(*args, **kwargs)
                    else:
                        raise e
                except ValueError as e:
                    if set_int_max_str:
                        str_e: str = str(e)
                        if 'Exceeds the limit ' in str_e and ' for integer string conversion: ' in str_e:
                            logger.info({'action': 'removing_int_max_str_limit'})
                            set_int_max_str_digits(0)
                            return func(*args, **kwargs)
                    raise e

            return wrapper_assign_on_exception

    return decorator
