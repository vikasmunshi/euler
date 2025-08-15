#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations


def human_readable_seconds(seconds: float) -> str:
    if seconds < 0:
        return f'-{human_readable_seconds(-seconds)}'
    if seconds >= 1:
        return f'{seconds:.2f} sec'
    elif seconds >= 1e-3:
        return f'{seconds * 1e3:.2f} milli-sec'
    elif seconds >= 1e-6:
        return f'{seconds * 1e6:.2f} micro-sec'
    else:
        return f'{seconds * 1e9:.2f} nano-sec'


def seconds_from_human_readable(human_readable: str) -> float:
    num, suffix = human_readable.split(' ', maxsplit=1)
    multiplier = {'sec': 1, 'milli-sec': 1e3, 'micro-sec': 1e6, 'nano-sec': 1e9}[suffix.strip()]
    return float(num) / multiplier
