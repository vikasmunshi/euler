#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Build shim: vendor ``README.md`` into the package tree at build time.

All project metadata lives in ``pyproject.toml``; this file exists for one job.

The start page renders the README below its cards, in **both** web tiers. The
content tier could read the repo's copy (it runs from a collaborator's clone),
but the auth tier cannot: ``euler-auth`` runs from the root-owned ``/opt/euler``
venv with ``ProtectHome=true`` and has no clone to read (see
``scripts/setup/auth.sh``). Serving the packaged copy in both tiers keeps one
code path and one text — the README is project documentation, not per-user
content, so a collaborator's branch must not change what the start page says.

So the file has to ship *inside* the distribution. Root ``README.md`` stays the
single source of truth (GitHub reads it there); ``solver/web/content/README.md``
is a build artifact — gitignored, never edited, regenerated on every build. It is
declared as package data in ``pyproject.toml``; this hook is what puts it there
before setuptools looks.

``build_py`` is the hook because every install path runs it: ``pip install .``
(the deployed venv, via scripts/setup/venv.sh), ``pip install -e .`` (the
developer venv — editable_wheel drives build_py to resolve the layout, so the
copy lands in the source tree the .pth points back at), and a plain wheel build.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

#: Root README → its home inside the package (alongside the assets Caddy deploys).
_SOURCE = Path(__file__).parent.resolve() / 'README.md'
_TARGET = Path(__file__).parent.resolve() / 'solver' / 'web' / 'content' / 'README.md'


class BuildPyWithReadme(build_py):
    """``build_py`` + the README copy, run before the package tree is collected."""

    def run(self) -> None:
        # Never silently ship a stale copy: a missing source is a broken build,
        # not a page that quietly loses its README six weeks from now.
        if not _SOURCE.is_file():
            raise FileNotFoundError(f'{_SOURCE} is missing — the start page renders it')
        _TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_SOURCE, _TARGET)
        super().run()


setup(cmdclass={'build_py': BuildPyWithReadme})
