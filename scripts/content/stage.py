#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage the euler-content wheel source: `content/` plus the public tree, in a scratch directory.

    python scripts/content/stage.py OUT_DIR      # then: pip install OUT_DIR

Copies `content/` to *OUT_DIR*, lays the public tree into `OUT_DIR/euler_content/tree/` and
stamps `_version.py` from `packages/solver/solver/version.py` (docs/package-guide.md § 4.1, § 5.2). Only **tracked**
files under the public roots are copied — an untracked scratch file never ships — and the
working-tree copy is what ships, as with the code the same deploy installs. Anything under
`solutions/private` is refused outright: that tree is not public, and must not be in a package
whatever else goes wrong. Stdlib-only; run as the checkout's owner (git refuses a repository
another uid owns), then install the result as whoever owns the target venv.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: The public paths, repo-relative: a file, or a directory taken whole.
PUBLIC: tuple[str, ...] = (
    'README.md', 'LICENSE',
    'docs/', 'topics/',
    'solutions/public/', 'solutions/problems.json',
    'packages/solver/solver/templates/',                                  # linked from the docs (/docs/file/)
    'packages/solver/solver/ai/claude/skills/',                           # composed into /docs/ai
    'packages/site/euler_site/content/home-summary.md', 'packages/site/euler_site/content/vendor/README.md',
)
PRIVATE: str = 'solutions/private/'


def public_files(root: Path = ROOT) -> list[str]:
    """The tracked files under :data:`PUBLIC`, repo-relative; raises if one is private."""
    listed = subprocess.run(['git', '-C', str(root), 'ls-files', '-z', '--', *PUBLIC],
                            check=True, capture_output=True).stdout.decode('utf-8')
    files = sorted(name for name in listed.split('\0') if name)
    leaked = [name for name in files if name.startswith(PRIVATE)]
    if leaked:
        raise SystemExit(f'stage: refusing — {len(leaked)} private file(s) under the public roots')
    return files


def version(root: Path = ROOT) -> str:
    """The code's version — the content's too (lockstep)."""
    version_file = root / 'packages' / 'solver' / 'solver' / 'version.py'
    match = re.search(r"__version__\s*=\s*'([^']+)'", version_file.read_text(encoding='utf-8'))
    if match is None:
        raise SystemExit('stage: no __version__ in packages/solver/solver/version.py')
    return match.group(1)


def stage(out: Path, root: Path = ROOT) -> int:
    """Build the wheel source in *out* (replaced if present); the number of files laid down."""
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(root / 'content', out, ignore=shutil.ignore_patterns('tree', '_version.py', '__pycache__',
                                                                         '*.egg-info', 'build'))
    tree = out / 'euler_content' / 'tree'
    files = public_files(root)
    for name in files:
        source = root / name
        if not source.is_file():                     # tracked but deleted in the working tree
            continue
        target = tree / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (out / 'euler_content' / '_version.py').write_text(f"__version__ = '{version(root)}'\n", encoding='utf-8')
    return len(files)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    count = stage(Path(argv[0]).absolute())
    print(f'staged euler-content {version()} ({count} files) in {argv[0]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
