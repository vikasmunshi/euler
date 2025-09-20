#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration for Project Euler.

This module provides JSON-formatted logging.
"""
from __future__ import annotations

import datetime
import json
import logging
import sys
from typing import Any, Dict

__all__ = ['logger']

# Declaration with type annotation only
logger: logging.Logger

try:  # Check if the logger is already defined
    # noinspection PyUnboundLocalVariable
    logger
except NameError:
    # Custom JSON formatter for logging
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record: Dict[str, Any] = {
                'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
                'level': record.levelname,
                'name': record.name,
                'message': record.getMessage(),
            }
            # Add exception info if available
            if record.exc_info:
                log_record['exception'] = self.formatException(record.exc_info)

            return json.dumps(log_record)

    def get_logger(name: str) -> logging.Logger:
        """Get a logger configured with JSON formatting.

        Args:
            name: The name of the logger, typically __name__

        Returns:
            A configured logger instance
        """
        # Create stdout handler for DEBUG and INFO levels
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(JsonFormatter())
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)

        # Create stderr handler for WARNING, ERROR, and CRITICAL levels
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(JsonFormatter())
        stderr_handler.setLevel(logging.WARNING)

        # Configure the logger
        __logger = logging.getLogger(name)
        __logger.setLevel(logging.INFO)

        # Remove any existing handlers
        __logger.handlers = []

        # Add our handlers
        __logger.addHandler(stdout_handler)
        __logger.addHandler(stderr_handler)

        return __logger
    logger = get_logger(__package__)
