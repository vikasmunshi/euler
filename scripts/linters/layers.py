#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The layering guard: the solver shell must not import the web tier.

docs/package-split.md § 3.1 — dependencies point one way, web → solver. Until the physical
split (phase 6) both halves share the `solver` package, so this checker draws the line:
every module under `solver/` that is not itself *web-side* (:data:`WEB_SIDE`) may not import
a web-side module — top-level or lazily inside a function, `import x` or `from x import y`.
The loader manifest (`solver/modules.csv`) counts too: a web-side command module listed
there is loaded into every shell.

Today's violations are recorded in `layers.allow` (one `<path> <module>` per line). The
allowlist only ratchets down: a new violation fails, and so does an entry that no longer
matches anything, so a phase that removes a coupling must also remove its line.

Usage: `python scripts/linters/layers.py [repo_root]` — exits 0 when clean.
"""
from __future__ import annotations

import ast
import csv
import sys
from pathlib import Path

#: Modules that belong to the web tier (and the packages it will become).
WEB_SIDE: tuple[str, ...] = ('solver.web', 'solver.auth.roster', 'euler_site', 'euler_webshell')
#: The allowlist, next to this script.
ALLOW_FILE: Path = Path(__file__).with_name('layers.allow')
#: The loader manifest, repo-relative.
MANIFEST: str = 'solver/modules.csv'

Violation = tuple[str, str]  # (repo-relative path, imported web-side module)


def is_web_side(module: str) -> bool:
    """True if *module* is, or lives under, a web-side module."""
    return any(module == web or module.startswith(f'{web}.') for web in WEB_SIDE)


def module_of(root: Path, path: Path) -> str:
    """The dotted module name of *path* (a `.py` file under *root*)."""
    parts = path.relative_to(root).with_suffix('').parts
    return '.'.join(parts[:-1] if parts[-1] == '__init__' else parts)


def imported_modules(tree: ast.AST) -> set[str]:
    """Every absolute module a parsed file imports, anywhere in it.

    `from a.b import c` yields `a.b`, or — when `a.b` is not itself web-side — `a.b.c`, since
    `c` may be a submodule (`from solver.core import osc`). A name that is not a submodule
    cannot match a web-side module it does not already sit under.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            if is_web_side(node.module):
                found.add(node.module)
            else:
                found.update(f'{node.module}.{alias.name}' for alias in node.names)
    return found


def violations(root: Path) -> set[Violation]:
    """Every web-side import made from the solver side of *root*, plus manifest rows."""
    found: set[Violation] = set()
    for path in sorted((root / 'solver').rglob('*.py')):
        if is_web_side(module_of(root, path)):
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        rel = path.relative_to(root).as_posix()
        found.update((rel, module) for module in imported_modules(tree) if is_web_side(module))
    manifest = root / MANIFEST
    if manifest.exists():
        with open(manifest, newline='') as f:
            next(csv.reader(f), None)
            for row in csv.reader(f):
                if len(row) > 1 and row[1].strip().lower() in ('true', '1', 'yes') and is_web_side(row[0]):
                    found.add((MANIFEST, row[0]))
    return found


def read_allow(path: Path) -> set[Violation]:
    """The allowlisted `(path, module)` pairs; `#` starts a comment."""
    allowed: set[Violation] = set()
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            fields = line.split('#', 1)[0].split()
            if len(fields) == 2:
                allowed.add((fields[0], fields[1]))
    return allowed


def check(root: Path, allow_file: Path = ALLOW_FILE) -> int:
    """Report new violations and stale allowlist entries; 0 when there are neither."""
    found, allowed = violations(root), read_allow(allow_file)
    new, stale = sorted(found - allowed), sorted(allowed - found)
    for rel, module in new:
        print(f'{rel}: imports web-side {module}')
    for rel, module in stale:
        print(f'{allow_file.name}: stale entry "{rel} {module}" — remove it')
    if new:
        print('^ the solver shell must not depend on the web tier (docs/package-split.md § 3.1)')
    return 1 if new or stale else 0


if __name__ == '__main__':
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()))
