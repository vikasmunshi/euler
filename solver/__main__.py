#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Entry point: runs the interactive solver shell."""

if __name__ == '__main__':
    from solver.cli import cli

    raise SystemExit(cli())
