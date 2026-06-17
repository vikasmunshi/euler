#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Shell framework (prompt-toolkit + rich): the readline → lexer → parser → interpreter pipeline.

Pipeline (see `docs/syntax.md` for the authoritative language reference):

    readline → lexer → parser → interpreter

plus a self-contained command framework (`command`, `register`, `console`) and
the `SolverShell` that ties it together.
"""
from __future__ import annotations

__all__ = [
    'SolverShell',
    'console',
    'register',
]

from solver.shell.register import register
from solver.shell.shell import SolverShell
from solver.shell.tty import console
