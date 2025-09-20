#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File Lock"""
from __future__ import annotations

from fcntl import LOCK_EX, LOCK_SH, LOCK_UN, flock
from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import Literal, cast

from euler_solver.framework.logger import logger


class FileLock:
    __slots__ = ('access_mode', 'file', 'file_path', 'type_lock')

    def __init__(self, file_path: Path, type_lock: Literal['read', 'write'] = 'read'):
        self.access_mode: str = 'w' if type_lock == 'write' else 'r'
        self.file: TextIOWrapper | None = None
        self.file_path: Path = file_path
        self.type_lock: int = LOCK_EX if type_lock == 'write' else LOCK_SH

    def __enter__(self) -> TextIOWrapper:
        if self.file is None:
            self.file = cast(TextIOWrapper, self.file_path.open(self.access_mode))
            logger.debug({'action': 'file open', 'file_path': self.file_path, 'access_mode': self.access_mode})
            flock(self.file.fileno(), self.type_lock)
            logger.debug({'action': 'file locked', 'file_path': self.file_path, 'access_mode': self.access_mode})
            return self.file
        else:
            raise RuntimeError('File is already locked')

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 tb: TracebackType | None) -> None:
        if self.file is not None:
            flock(self.file.fileno(), LOCK_UN)
            logger.debug({'action': 'file unlocked', 'file_path': self.file_path, 'access_mode': self.access_mode})
            self.file.close()
            logger.debug({'action': 'file closed', 'file_path': self.file_path, 'access_mode': self.access_mode})
            self.file = None
