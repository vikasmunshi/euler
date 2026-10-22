#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The layering guard: dependencies between the three packages point one way.

docs/package-guide.md § 1 — `euler_webshell → euler_site → solver`. Each package lives in
its own folder under `packages/`; this checker reads every module of each and fails on an
import of a package *above* it — top-level or lazily inside a function, `import x` or
`from x import y`:

- `packages/solver/solver` may import neither `euler_site` nor `euler_webshell`;
- `packages/site/euler_site` may not import `euler_webshell`.

The solver's loader manifest (`packages/solver/solver/modules.csv`) counts too: a command
module listed there is loaded into every shell, so it may name only the solver's own.

Known exceptions would be recorded in `layers.allow` (one `<path> <module>` per line); it is
empty, and it only ratchets down: a new violation fails, and so does an entry that no longer
matches anything.

Usage: `python scripts/linters/layers.py [repo_root]` — exits 0 when clean.
"""
from __future__ import annotations

import ast
import csv
import sys
from pathlib import Path

#: (the package's folder in the checkout, its import name, the packages it may not import).
LAYERS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ('packages/solver', 'solver', ('euler_site', 'euler_webshell')),
    ('packages/site', 'euler_site', ('euler_webshell',)),
)
#: The allowlist, next to this script.
ALLOW_FILE: Path = Path(__file__).with_name('layers.allow')
#: The loader manifest, repo-relative, and the one package it may name.
MANIFEST: str = 'packages/solver/solver/modules.csv'
MANIFEST_PACKAGE: str = 'solver'

Violation = tuple[str, str]  # (repo-relative path, imported module from a higher layer)


def is_under(module: str, packages: tuple[str, ...]) -> bool:
    """True if *module* is, or lives under, one of *packages*."""
    return any(module == pkg or module.startswith(f'{pkg}.') for pkg in packages)


def imported_modules(tree: ast.AST) -> set[str]:
    """Every absolute module a parsed file imports, anywhere in it.

    `from a import b` yields `a` and `a.b` — `b` may be a submodule — so a check on either
    form of a forbidden package catches it.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module)
    return found


def violations(root: Path) -> set[Violation]:
    """Every import of a higher layer, from every package of *root*, plus manifest rows."""
    found: set[Violation] = set()
    for folder, name, forbidden in LAYERS:
        for path in sorted((root / folder / name).rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            rel = path.relative_to(root).as_posix()
            found.update((rel, module) for module in imported_modules(tree) if is_under(module, forbidden))
    manifest = root / MANIFEST
    if manifest.exists():
        with open(manifest, newline='') as f:
            next(csv.reader(f), None)
            for row in csv.reader(f):
                if len(row) > 1 and row[1].strip().lower() in ('true', '1', 'yes') \
                        and not is_under(row[0], (MANIFEST_PACKAGE,)):
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
        print(f'{rel}: imports {module}, a layer above it')
    for rel, module in stale:
        print(f'{allow_file.name}: stale entry "{rel} {module}" — remove it')
    if new:
        print('^ dependencies point one way: euler_webshell → euler_site → solver (docs/package-guide.md § 1)')
    return 1 if new or stale else 0


if __name__ == '__main__':
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()))
