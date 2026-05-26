#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Module for the solver shell."""
from __future__ import annotations

import solver.shell.builtins  # noqa: F401
from solver.shell.commands import register
from solver.shell.shell import SolverShell, command, console

__all__ = (
    'SolverShell',
    'command',
    'console',
    'register',
)
