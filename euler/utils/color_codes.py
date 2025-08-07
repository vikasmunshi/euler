#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Color Codes"""
from __future__ import annotations

from enum import StrEnum


class Color(StrEnum):
    """Color codes for console output."""
    GREEN = '\033[92m'  # Light Green
    YELLOW = '\033[93m'  # Light Yellow
    RED = '\033[91m'  # Light Red
    ORANGE = '\033[38;5;208m'  # Orange
    BLUE = '\033[94m'  # Light Blue
    CYAN = '\033[96m'  # Light Cyan
    MAGENTA = '\033[95m'  # Light Magenta
    WHITE = '\033[97m'  # White
    BLACK = '\033[30m'  # Black
    GRAY = '\033[90m'  # Gray
    BOLD = '\033[1m'  # Bold Text
    UNDERLINE = '\033[4m'  # Underline
    RESET = '\033[0m'  # Reset format
