#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The save gate: the checks every write passes.

One entry point — :func:`validate` — dispatches on the file's suffix and returns
the **canonical bytes to store** (which may differ from the submission) or the
failure diagnostics; the edit routes wire it in front of every write:

- ``.py``   — auto-fix (autoflake → autopep8 → isort, best-effort: the ``dev``
  extras may be absent in the deployed venv) then **flake8 over stdin**;
  reject on findings. The fixed source is the canonical content.
- ``.c``    — compile with gcc against the runner header (``solver/runners``)
  in a scratch dir, mirroring ``scripts/c/compile.sh``'s flags and extra-lib
  detection; reject on any diagnostic (``-Werror``). The binary is discarded —
  the gate only proves compilability; the real build happens at evaluation.
- ``.json`` — parse; reject when malformed. The two-space re-indent is the
  canonical content.
- ``.html`` — **sanitize-and-store-clean via nh3**: the tailored
  allowlist below, MathJax ``$…$`` surviving as text, ``rel`` rewritten on every
  link. nh3's output is *always* the canonical content (it normalises even clean
  input — adds ``<tbody>``, rewrites ``rel`` — which is why this is store-clean,
  not reject-and-restore); the editor shows the submitted-vs-stored diff. nh3
  gates what is *stored*; the CSP (§4.7) blocks what would *execute*.

Like the rest of the service this module never touches
:mod:`solver.config`: the repo root arrives explicitly and the only paths read
are the runner header and the submitted content.
"""
from __future__ import annotations

__all__ = ['Validated', 'Diagnostic', 'EDITABLE_SUFFIXES', 'validate']

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, NamedTuple

import nh3

#: The project line-length contract (flake8 + autopep8), fixed repo-wide.
_MAX_LINE_LENGTH = 120

#: Ceiling on any checker subprocess — a hung gcc/flake8 must not wedge a worker.
_CHECK_TIMEOUT = 60.0

#: The suffixes the editor may save; anything else is rejected outright.
EDITABLE_SUFFIXES: frozenset[str] = frozenset({'.py', '.c', '.json', '.html'})

#: The nh3 allowlist: the `convention_documentation.md` semantic-HTML5 set
#: as the notes corpus actually uses it, plus the table internals nh3 itself
#: normalises in (`thead`/`tbody`) and `ol`/`pre` as their semantic companions.
_HTML_TAGS: frozenset[str] = frozenset({
    'article', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
    'tr', 'th', 'td', 'code', 'pre', 'a', 'strong', 'em', 'sup', 'sub', 'br',
})
#: `a` keeps its class/target/href; `rel` is nh3-managed (link_rel) on every link.
_HTML_ATTRIBUTES: dict[str, set[str]] = {'a': {'href', 'class', 'target'}}
_HTML_LINK_REL = 'noopener noreferrer'


class Diagnostic(NamedTuple):
    """One checker finding, positioned for the editor's line markers."""

    line: int
    col: int
    severity: str  # 'error' | 'warning'
    message: str


class Validated(NamedTuple):
    """The gate's verdict: canonical bytes to store, or why the save is refused."""

    ok: bool
    content: bytes            # on ok: the canonical bytes (may differ from the submission)
    message: str              # short human summary (the failure reason when not ok)
    diagnostics: list[Diagnostic]


def _fail(message: str, diagnostics: list[Diagnostic] | None = None) -> Validated:
    return Validated(ok=False, content=b'', message=message, diagnostics=diagnostics or [])


# ── diagnostics parsing (flake8 / gcc text → line markers) ─────────────────────────

#: flake8 line: `path:row:col: CODE message`.
_FLAKE8_RE = re.compile(r'^.*?:(\d+):(\d+):\s+([A-Z]\d+)\s+(.*)$')
#: gcc line: `path:row[:col]: error|warning|note: message`.
_GCC_RE = re.compile(r'^.*?:(\d+):(?:(\d+):)?\s+(error|warning|note):\s+(.*)$')


def _parse_diagnostics(output: str, suffix: str) -> list[Diagnostic]:
    """Parse flake8 / gcc text into positioned diagnostics.

    Non-matching lines (summary banners, multi-line context) are ignored. flake8
    `F*` / `E9*` (pyflakes + syntax) map to errors, the rest to warnings; gcc maps
    by the emitted severity word (a `note` becomes a warning).
    """
    diagnostics: list[Diagnostic] = []
    if suffix == '.py':
        for line in output.splitlines():
            if (m := _FLAKE8_RE.match(line)) is None:
                continue
            code = m.group(3)
            severity = 'error' if code.startswith('F') or code.startswith('E9') else 'warning'
            diagnostics.append(Diagnostic(int(m.group(1)), int(m.group(2)),
                                          severity, f'{code} {m.group(4)}'))
    else:
        for line in output.splitlines():
            if (m := _GCC_RE.match(line)) is None:
                continue
            severity = 'error' if m.group(3) == 'error' else 'warning'
            diagnostics.append(Diagnostic(int(m.group(1)), int(m.group(2) or 1),
                                          severity, m.group(4)))
    return diagnostics


# ── per-suffix gates ────────────────────────────────────────────────────────────────

def _lazy_fix_code() -> Callable[[str], str] | None:
    """A source-fixing callable (autoflake → autopep8 → isort), or None.

    The `dev`-group tools are imported on demand: the deployed system venv
    carries only the `web` extra, where the gate degrades to check-only.
    """
    try:
        import autoflake
        import autopep8
        import isort
    except ImportError:
        return None

    def fix_code(source: str) -> str:
        code = autoflake.fix_code(source, remove_all_unused_imports=True, remove_duplicate_keys=True)
        code = autopep8.fix_code(code, options={'max_line_length': _MAX_LINE_LENGTH})
        code = isort.code(code, profile='black', line_length=_MAX_LINE_LENGTH)
        return code

    return fix_code


def _validate_python(filename: str, content: bytes, repo_root: Path) -> Validated:
    """Auto-fix (best-effort), then flake8 over stdin; the fixed source is canonical."""
    try:
        source = content.decode('utf-8')
    except UnicodeDecodeError as exc:
        return _fail(f'{filename} is not valid UTF-8: {exc}')
    if (fix_code := _lazy_fix_code()) is not None:
        try:
            source = fix_code(source)
        except Exception:  # noqa: BLE001 — broken source: skip the fixer, flake8 reports below
            pass
    try:
        proc = subprocess.run(
            [sys.executable, '-m', 'flake8', f'--max-line-length={_MAX_LINE_LENGTH}',
             '--stdin-display-name', filename, '-'],
            input=source, capture_output=True, text=True, cwd=repo_root, timeout=_CHECK_TIMEOUT)
    except subprocess.TimeoutExpired:
        return _fail(f'flake8 timed out on {filename}')
    if proc.returncode != 0:
        output = (proc.stdout + ('\n' if proc.stdout and proc.stderr else '') + proc.stderr).strip()
        return _fail(output or f'{filename} failed flake8',
                     _parse_diagnostics(output, '.py'))
    return Validated(ok=True, content=source.encode('utf-8'),
                     message=f'saved {filename}', diagnostics=[])


def _validate_c(filename: str, content: bytes, repo_root: Path) -> Validated:
    """Compile in a scratch dir with `scripts/c/compile.sh`'s flags; discard the binary."""
    source = content.decode('utf-8', errors='replace')
    # The compile script's extra-lib detection, kept in step (bignum + primesieve).
    extra_libs: list[str] = []
    if re.search(r'^#include\s*<primesieve\.h>', source, re.MULTILINE):
        extra_libs.append('-lprimesieve')
    if re.search(r'^#include\s*<mpfr\.h>', source, re.MULTILINE):
        extra_libs += ['-lmpfr', '-lgmp']
    elif re.search(r'^#include\s*<gmp\.h>', source, re.MULTILINE):
        extra_libs.append('-lgmp')
    if re.search(r'^#include\s*<openssl/bn\.h>', source, re.MULTILINE):
        extra_libs.append('-lcrypto')
    runner_include = repo_root / 'solver' / 'runners'
    with tempfile.TemporaryDirectory(prefix='euler-cgate-') as scratch:
        src = Path(scratch) / Path(filename).name
        src.write_bytes(content)
        try:
            proc = subprocess.run(
                ['gcc', '-O2', '-Werror', f'-I{runner_include}', '-o',
                 str(src.with_suffix('')), str(src), '-lm', *extra_libs],
                capture_output=True, text=True, timeout=_CHECK_TIMEOUT)
        except subprocess.TimeoutExpired:
            return _fail(f'gcc timed out on {filename}')
        except FileNotFoundError:
            return _fail('gcc is not available to the content service')
    if proc.returncode != 0:
        output = (proc.stdout + ('\n' if proc.stdout and proc.stderr else '') + proc.stderr).strip()
        output = output.replace(str(src), Path(filename).name)  # scratch paths → the filename
        return _fail(output or f'{filename} failed to compile',
                     _parse_diagnostics(output, '.c'))
    return Validated(ok=True, content=content, message=f'saved {filename}', diagnostics=[])


def _validate_json(filename: str, content: bytes) -> Validated:
    """Parse; the two-space re-indent is the canonical content."""
    try:
        canonical = json.dumps(json.loads(content), indent=2, ensure_ascii=False).encode('utf-8')
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _fail(f'{filename} is not valid JSON: {exc}')
    return Validated(ok=True, content=canonical, message=f'saved {filename}', diagnostics=[])


def _sanitize_html(filename: str, content: bytes) -> Validated:
    """nh3 sanitize-and-store-clean: the sanitised output is canonical."""
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError as exc:
        return _fail(f'{filename} is not valid UTF-8: {exc}')
    clean = nh3.clean(text, tags=set(_HTML_TAGS), attributes=dict(_HTML_ATTRIBUTES),
                      link_rel=_HTML_LINK_REL)
    return Validated(ok=True, content=clean.encode('utf-8'),
                     message=f'saved {filename} (sanitised)', diagnostics=[])


# ── entry point ─────────────────────────────────────────────────────────────────────

def validate(filename: str, content: bytes, repo_root: Path) -> Validated:
    """Gate one submitted file: canonical bytes to store, or the refusal.

    *filename* is the bare solution-directory name (used for display and the
    suffix dispatch); *content* is the submitted bytes; *repo_root* locates the
    runner header for the C compile. An unknown suffix is refused.
    """
    suffix = Path(filename).suffix
    match suffix:
        case '.py':
            return _validate_python(filename, content, repo_root)
        case '.c':
            return _validate_c(filename, content, repo_root)
        case '.json':
            return _validate_json(filename, content)
        case '.html':
            return _sanitize_html(filename, content)
        case _:
            return _fail(f'{filename} is not an editable solution file')
