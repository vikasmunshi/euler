#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""JSON persistence for the auth stores — re-export of the shared implementation.

The atomic ``0600`` writer moved to :mod:`solver.web.store` when the message spool
gained its own state dir and needed the identical guarantees. Auth's stores keep
importing it from here; the semantics are unchanged (the service is the sole reader
and writer of every file in its private state dir).
"""
from __future__ import annotations

__all__ = ['load_json', 'save_json']

from solver.web.store import load_json, save_json
