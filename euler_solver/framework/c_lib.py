#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""C library utilities for managing and importing compiled C functions.

This module provides functionality to:
- Import functions from compiled C libraries (.dll, .dylib, .so)
- Wrap C functions with Python decorators for seamless integration
- Handle platform-specific library extensions
"""
from __future__ import annotations

import ctypes
import inspect
from functools import wraps
from typing import Any, Callable, ClassVar, ParamSpec, TypeVar

from euler_solver.framework.logger import logger
from euler_solver.framework.paths import get_c_lib_path

PS = ParamSpec('PS')
RT = TypeVar('RT')
FS = Callable[PS, RT]


class WrappedCFunction:
    use_py_func: ClassVar[bool] = False

    def __init__(self, *, py_func: FS, c_func: FS | None) -> None:
        self.c_func: FS = py_func if c_func is None else c_func
        self.py_func: FS = py_func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.__class__.use_py_func:
            return self.py_func(*args, **kwargs)
        return self.c_func(*args, **kwargs)


def import_c_lib(euler_problem: int) -> ctypes.CDLL:
    if not (lib_path := get_c_lib_path(euler_problem)).exists():
        raise ImportError(f'C library {lib_path} does not exist.')
    try:
        # Load with RTLD_GLOBAL to allow symbol resolution across shared libs
        mode = getattr(ctypes, 'RTLD_GLOBAL', None)
        lib = ctypes.CDLL(lib_path.as_posix(), mode=mode) if mode is not None else ctypes.CDLL(lib_path.as_posix())
        return lib
    except OSError as e:
        logger.error(f'Failed to load C library {lib_path}: {e}')
        raise ImportError(f'Failed to load C library {lib_path}. '
                          f'Make sure the library is compiled and installed correctly: {e}')


def use_c_function(loader: Callable[[], tuple[Callable, ...]], index: int = 0) -> Callable[[FS[PS, RT]], FS[PS, RT]]:
    def decorator(py_func: FS[PS, RT]) -> FS[PS, RT]:
        c_funcs: tuple[Callable, ...] = loader()
        c_func: Callable = c_funcs[index]
        if (py_sig := inspect.signature(py_func)) != (c_sig := inspect.signature(c_func)):
            raise TypeError(f"Function signatures don't match: Python {py_sig} != C {c_sig}")
        return wraps(py_func)(WrappedCFunction(py_func=py_func, c_func=c_func))

    return decorator


def set_use_py_func(use_py_func: bool) -> None:
    WrappedCFunction.use_py_func = use_py_func


def get_use_py_func() -> bool:
    return WrappedCFunction.use_py_func
