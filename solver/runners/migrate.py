#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrate legacy solutions to the new runner framework."""
from __future__ import annotations

__all__ = ['migrate']

import ast
import re
import textwrap
from pathlib import Path
from typing import Callable, Literal

from solver.config import ExitCodes, config
from solver.core.evaluate import _evaluate
from solver.core.lock import check_workspace_lock_command
from solver.shell import console, register
from solver.shell.variables import variables
from solver.utils.path_utils import iterdir_recursive

# ==================================================================================================================== #
#                                                 C migration                                                          #
# ==================================================================================================================== #

# Standard headers that runner.h already pulls in — dropped in favour of `#include "runner.h"`.
RUNNER_C_INCLUDES: frozenset[str] = frozenset({'stdio.h', 'stdlib.h', 'string.h', 'time.h', 'libgen.h', 'unistd.h'})

# Legacy C helper functions that runner.h now provides — deleted so they don't clash/redefine.
RUNNER_C_FUNCTIONS: tuple[str, ...] = ('main', 'get_text_file', 'parse_int', 'parse_list')

# Global text rewrites on the assembled C source (parse args via the runner helper, like Python).
C_REPLACEMENTS: list[tuple[str, str]] = [
    (r'\batoll\(\s*argv', 'parse_int(argv'),
    (r'\batoi\(\s*argv', 'parse_int(argv'),
    (r'(get_text_file\([^,()]*),[^()]*\)', r'\1)'),  # legacy 2-arg get_text_file(src, argv[0]) -> 1-arg
]


def _c_match_brace(src: str, open_idx: int) -> int:
    """Index of the `}` matching the `{` at open_idx, skipping strings, chars and comments."""
    depth: int = 0
    i: int = open_idx
    n: int = len(src)
    while i < n:
        pair: str = src[i:i + 2]
        if pair == '//':
            nl: int = src.find('\n', i)
            i = n if nl < 0 else nl + 1
            continue
        if pair == '/*':
            end: int = src.find('*/', i + 2)
            i = n if end < 0 else end + 2
            continue
        c: str = src[i]
        if c in '"\'':
            i += 1
            while i < n and src[i] != c:
                i += 2 if src[i] == '\\' else 1
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _delete_start(src: str, start: int) -> int:
    """Move a deletion start back over an immediately-preceding block comment (e.g. a function's
    doc comment), so deleting main()/get_text_file() takes its `/* ... */` header with it."""
    j: int = start
    while j > 0 and src[j - 1] in ' \t\n':
        j -= 1
    if j >= 2 and src[j - 2:j] == '*/' and (open_idx := src.rfind('/*', 0, j)) >= 0:
        return src.rfind('\n', 0, open_idx) + 1
    return start


def _c_skip(src: str, i: int) -> int | None:
    """If src[i] starts a comment/string/char literal, return the index just past it; else None."""
    pair: str = src[i:i + 2]
    if pair == '//':
        nl: int = src.find('\n', i)
        return len(src) if nl < 0 else nl + 1
    if pair == '/*':
        end: int = src.find('*/', i + 2)
        return len(src) if end < 0 else end + 2
    if src[i] in '"\'':
        quote: str = src[i]
        j: int = i + 1
        while j < len(src) and src[j] != quote:
            j += 2 if src[j] == '\\' else 1
        return j + 1
    return None


def _c_is_func_def_brace(body: str, brace: int) -> bool:
    """True if the `{` at index `brace` opens a nested function body — `name(params) {` where
    `name` is an identifier other than a control keyword. Used to skip GCC nested functions
    (e.g. a qsort comparator) whose returns must NOT be captured as solve()'s answer."""
    j: int = brace - 1
    while j >= 0 and body[j] in ' \t\n':
        j -= 1
    if j < 0 or body[j] != ')':
        return False
    depth: int = 0
    while j >= 0:  # walk back to the matching '('
        if body[j] == ')':
            depth += 1
        elif body[j] == '(':
            depth -= 1
            if depth == 0:
                break
        j -= 1
    if j < 0:
        return False
    end: int = j
    while end > 0 and body[end - 1] in ' \t\n':
        end -= 1
    start: int = end
    while start > 0 and (body[start - 1].isalnum() or body[start - 1] == '_'):
        start -= 1
    name: str = body[start:end]
    return bool(name) and name not in ('if', 'for', 'while', 'switch')


def _wrap_c_returns(body: str) -> str:
    """Wrap each `return EXPR;` into the shared `_answer` buffer, skipping comments and strings."""
    out: list[str] = []
    i: int = 0
    n: int = len(body)
    while i < n:
        if (nxt := _c_skip(body, i)) is not None:
            out.append(body[i:nxt])
            i = nxt
            continue
        if body[i] == '{' and _c_is_func_def_brace(body, i):  # skip a nested function body verbatim
            close: int = _c_match_brace(body, i)
            close = close if close >= 0 else n - 1
            out.append(body[i:close + 1])
            i = close + 1
            continue
        is_word = lambda ch: ch.isalnum() or ch == '_'  # noqa: E731
        if (body.startswith('return', i)
                and (i == 0 or not is_word(body[i - 1]))
                and (i + 6 >= n or not is_word(body[i + 6]))):
            k: int = i + 6
            while k < n and not (body[k] == ';' and _c_skip(body, k) is None):
                k = nxt2 if (nxt2 := _c_skip(body, k)) is not None else k + 1
            expr: str = body[i + 6:k].strip()
            out.append(f'{{ snprintf(_answer, sizeof _answer, "%lld", (long long)({expr})); return _answer; }}')
            i = k + 1
            continue
        out.append(body[i])
        i += 1
    return ''.join(out)


def _c_function(src: str, name: str) -> tuple[int, int, int, str] | None:
    """Locate a C function definition: returns (def_start, open_brace, close_brace, return_type)."""
    pattern = re.compile(r'(?m)^([A-Za-z_][\w \t*]*?)\b' + re.escape(name) + r'\s*\([^;{}]*\)\s*\{')
    if (m := pattern.search(src)) is None:
        return None
    open_idx: int = m.end() - 1  # the '{'
    if (close_idx := _c_match_brace(src, open_idx)) < 0:
        return None
    return m.start(), open_idx, close_idx, m.group(1).strip()


def _migrate_c(c_file: Path) -> bool:
    """Rewrite a legacy C solution in place: drop main()/get_text_file(), retype solve() to
    `const char *`, wrap numeric returns into a static buffer, and switch to runner.h."""
    src: str = c_file.read_text()
    if (solve := _c_function(src, 'solve')) is None:
        console.print(f'[error]{c_file.name}: no solve(int argc, char *argv[]) function — migrate by hand.[/error]')
        return False
    s_start, s_open, s_close, s_rettype = solve
    if 'void' in s_rettype.split():  # solve prints/returns nothing — incompatible with the runner contract
        console.print(f'[error]{c_file.name}: solve() returns void (prints directly) — migrate by hand.[/error]')
        return False

    # Char-span edits: (start, end_exclusive, replacement); applied back-to-front so offsets hold.
    edits: list[tuple[int, int, str]] = []
    for fn_name in RUNNER_C_FUNCTIONS:
        if (fn := _c_function(src, fn_name)) is not None:
            edits.append((_delete_start(src, fn[0]), fn[2] + 1, ''))  # delete function + its doc comment

    edits.append((s_start, s_open, 'const char *solve(int argc, char *argv[]) '))  # normalise signature

    if 'char' not in s_rettype:  # numeric solve: capture each return into a shared static buffer
        body: str = src[s_open + 1:s_close]
        edits.append((s_open + 1, s_close, '\n    static char _answer[32];' + _wrap_c_returns(body)))

    includes = list(re.finditer(r'(?m)^[ \t]*#include\s*[<"][^>"]+[>"][^\n]*\n', src))
    if includes:
        kept = [
            inc.group(0) for inc in includes
            if not any(f'<{h}>' in inc.group(0) for h in RUNNER_C_INCLUDES)
        ]
        edits.append((includes[0].start(), includes[-1].end(), '#include "runner.h"\n' + ''.join(kept)))

    for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        src = src[:start] + replacement + src[end:]
    for pattern_str, replacement_str in C_REPLACEMENTS:
        src = re.sub(pattern_str, replacement_str, src)
    c_file.write_text(src.rstrip() + '\n')  # deleting trailing main() leaves a blank line at EOF
    return True


# ==================================================================================================================== #
#                                                 PY migration                                                         #
# ==================================================================================================================== #

# Legacy helper functions that runner.* now provides — deleted so runner.<name> replaces them.
RUNNER_PY_FUNCTIONS: tuple[str, ...] = ('main', 'get_text_file', 'parse_int', 'parse_list')

# Map a legacy solve() parameter annotation to the runner helper that parses args[i].
ANNOTATION_PARSERS: dict[str, Callable[[int], str]] = {
    'int': lambda i: f'runner.parse_int(args[{i}])',
    'str': lambda i: f'args[{i}]',
    'float': lambda i: f'float(args[{i}])',
    'list': lambda i: f'runner.parse_list(args[{i}])',
    'tuple': lambda i: f'tuple(runner.parse_list(args[{i}]))',
}


def _annotation_name(annotation: ast.expr | None) -> str:
    """Base name of a parameter annotation: `int`, `list` (from `list[int]`), etc."""
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return annotation.value.id  # list[int] -> 'list'
    return ''


# Text rewrites applied to the assembled module. Seed list — extend as variants appear.
REPLACEMENTS: list[tuple[str, str]] = [
    (r'(?<![.\w])get_text_file\(', 'runner.get_text_file('),
    (r'(?<![.\w])parse_int\(', 'runner.parse_int('),
    (r'(?:sys\.)?argv\[-1\]\s*==\s*(["\'])--show\1', 'runner.show'),
    (r'(?:sys\.)?argv\[-1\]\s*!=\s*(["\'])--show\1', 'not runner.show'),
]


def _node_range(node: ast.stmt) -> tuple[int, int]:
    """1-indexed inclusive (start, end) line span of a top-level node, decorators included."""
    decorators: list[ast.expr] = getattr(node, 'decorator_list', [])
    start: int = min((d.lineno for d in decorators), default=node.lineno)
    return start, node.end_lineno or node.lineno


def _is_if_main(node: ast.stmt) -> bool:
    """True for an `if __name__ == "__main__":` guard block."""
    return (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == '__name__'
    )


def _collapse_blank_lines(text: str) -> str:
    """Collapse any run of 3+ blank lines to 2 (PEP 8 max) — deletions can leave gaps."""
    return re.sub(r'\n[ \t]*\n[ \t]*\n[ \t]*\n+', '\n\n\n', text)


def _wrap_top_level_returns(solve_src: str) -> str:
    """Wrap each of solve()'s own `return X` values in `str(...)` (skipping nested defs)."""
    fn = ast.parse(solve_src).body[0]
    targets: list[ast.expr] = []

    def walk(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue  # don't descend into nested scopes — their returns aren't solve()'s
            if isinstance(child, ast.Return) and child.value is not None:
                targets.append(child.value)
            walk(child)

    walk(fn)
    if not targets:
        return solve_src
    lines = solve_src.splitlines(keepends=True)
    starts: list[int] = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    spans = sorted(
        ((starts[v.lineno - 1] + v.col_offset, starts[(v.end_lineno or v.lineno) - 1] + (v.end_col_offset or 0))
         for v in targets),
        reverse=True,
    )
    out: str = solve_src
    for start, end in spans:
        out = f'{out[:start]}str({out[start:end]}){out[end:]}'
    return out


def _build_solve(src_lines: list[str], solve_node: ast.FunctionDef, prelude: list[str]) -> str:
    """Assemble the new `@runner.main def solve(*args)` from the legacy solve().

    `prelude` holds statements hoisted from the legacy `if __name__` block (e.g.
    `sys.setrecursionlimit(...)`) that must run before the body, now inside solve().
    """
    params = [*solve_node.args.posonlyargs, *solve_node.args.args, *solve_node.args.kwonlyargs]
    binds: list[str] = []
    for i, arg in enumerate(params):
        ann = _annotation_name(arg.annotation)
        if (parser := ANNOTATION_PARSERS.get(ann)) is not None:
            rhs = parser(i)
        else:
            rhs = f'args[{i}]'
            console.print(f'[warning]Unknown annotation for {arg.arg!r}; defaulting to args[{i}].[/warning]')
        binds.append(f'    {arg.arg} = {rhs}')
    body_start: int = solve_node.body[0].lineno
    body: str = '\n'.join(src_lines[body_start - 1:solve_node.end_lineno])
    prefix: list[str] = [*binds, *(textwrap.indent(stmt, '    ') for stmt in prelude)]
    lines: list[str] = ['@runner.main', 'def solve(*args: str) -> str:', *prefix]
    if prefix:
        lines.append('')  # blank line so a nested def in the body doesn't trip E306
    lines.append(body)
    return _wrap_top_level_returns('\n'.join(lines))


def _migrate_py(py_file: Path) -> bool:
    """Rewrite a legacy solution in place: surgical edits over the original lines, no reflow.

    Helpers and their formatting/comments stay untouched; only solve(), the legacy main()/
    get_text_file()/entry point, and the imports change. isort + autoflake tidy imports at the end.
    """
    try:  # dev-group deps, imported on demand so the shell starts without the `dev` group installed
        import autoflake
        import isort
    except ImportError as exc:
        console.print(f'[error]{py_file.name}: migrating Python solutions needs the [accent]dev[/accent] '
                      f'dependency group ({exc.name} is not installed) — '
                      f'run [accent]pip install -e ".\\[dev]"[/accent].[/error]')
        return False
    source: str = py_file.read_text()
    src_lines: list[str] = source.splitlines()
    tree = ast.parse(source)
    by_name: dict[str, ast.FunctionDef] = {
        n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)
    }
    if (solve_node := by_name.get('solve')) is None:
        console.print(f'[error]{py_file.name}: no top-level solve() found.[/error]')
        return False
    if_main = next((n for n in tree.body if isinstance(n, ast.If) and _is_if_main(n)), None)
    prelude: list[str] = [
        ast.unparse(stmt) for stmt in (if_main.body if if_main else []) if 'main(' not in ast.unparse(stmt)
    ]
    footer: str = 'if __name__ == "__main__":\n    raise SystemExit(solve())'

    # Each edit replaces the 1-indexed inclusive line span [lo, hi] with new lines.
    edits: list[tuple[int, int, list[str]]] = []
    s_lo, s_hi = _node_range(solve_node)
    edits.append((s_lo, s_hi, _build_solve(src_lines, solve_node, prelude).split('\n')))
    for name in RUNNER_PY_FUNCTIONS:
        if (node := by_name.get(name)) is not None:
            lo, hi = _node_range(node)
            edits.append((lo, hi, []))  # delete the legacy helper — runner.<name> replaces it
    if if_main is not None:
        lo, hi = _node_range(if_main)
        edits.append((lo, hi, footer.split('\n')))
    last_import = max(
        (n.end_lineno or n.lineno for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))),
        default=0,
    )
    edits.append((last_import + 1, last_import, ['from solver.runners import runner']))  # insert after imports

    out: list[str] = list(src_lines)
    for lo, hi, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        out[lo - 1:hi] = replacement
    code: str = '\n'.join(out) + '\n'
    for pattern, replacement_str in REPLACEMENTS:
        code = re.sub(pattern, replacement_str, code)
    code = autoflake.fix_code(code, remove_all_unused_imports=True, remove_duplicate_keys=True)
    code = isort.code(code, profile='black')
    code = _collapse_blank_lines(code)
    py_file.write_text(code)
    return True


# ==================================================================================================================== #
#                                                   Main                                                               #
# ==================================================================================================================== #
def _revert(orig: Path, backup: Path, keep_backup: bool) -> None:
    orig.write_bytes(backup.read_bytes())
    console.print(f'[success]Successfully reverted {orig.name} from backup.[/success]')
    if not keep_backup:
        backup.unlink()
        console.print(f'[success]Deleted backup file {backup.name}.[/success]')


migrators: dict[str, Callable[[Path], bool]] = {
    '.py': _migrate_py,
    '.c': _migrate_c
}
langs: dict[str, Literal['py', 'c']] = {
    '.py': 'py',
    '.c': 'c'
}
# Markers that a file is already on the runner framework — used to skip re-migration.
already_migrated_markers: dict[str, str] = {
    '.py': 'from solver.runners import runner',
    '.c': '#include "runner.h"',
}


def _already_migrated(f: Path) -> bool:
    """True if f already imports the runner framework (idempotency guard)."""
    return already_migrated_markers[f.suffix] in f.read_text()


@register(help_text='Migrate solutions in workspace to runner framework.')
@check_workspace_lock_command
def migrate(revert_on_failure: bool = True, keep_backup: bool = False) -> int:
    """Port the workspace's legacy solutions to the runner framework.

    Rewrites each `p<NNNN>_s<K>.py` / `.c` solution in the workspace to the
    `@runner.main` / `runner.h` interface — `solve()` plus the shared harness —
    in place, skipping files already migrated. A `.bak` copy of each original is
    made before editing.

    Requires the `dev` dependency group (autoflake/autopep8/black/isort) for the
    Python transform. Run `eval` afterwards to confirm parity; remember to fold
    any module-level cache into `solve()` so `--runs` benchmarks stay honest.

    Args:
        revert_on_failure:  When True (default), restore a file from its backup
                            if its migration fails, leaving the original intact.
        keep_backup:        When True, keep the `.bak` files after a successful
                            migration; when False (default), remove them.
    """
    if (problem := variables.problem) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return ExitCodes.EXIT_ERROR
    prefix: str = f'p{problem.number:04d}_s'
    source_files: list[Path] = []
    for f in iterdir_recursive(config.workspace_dir, rt='path'):
        if not (f.is_file() and f.name.startswith(prefix)):
            continue
        if f.suffix in ('.py', '.c'):
            source_files.append(f)
    rc: int = ExitCodes.EXIT_OK
    for f in sorted(source_files):
        if _already_migrated(f):
            console.print(f'[muted]{f.name} already on the runner framework, skipping.[/muted]')
            continue
        console.print(f'[muted]Migrating {f.name} to runner framework...[/muted]')
        backup_file: Path = f.with_suffix(f'{f.suffix}.bak')
        backup_file.write_bytes(f.read_bytes())
        migrated: bool = migrators[f.suffix](f)
        if migrated:
            console.print(f'[success]Successfully migrated {f.name} to runner framework.[/success]')
            result: int = _evaluate(
                clean=True,
                disable_timeout=False,
                lang=langs[f.suffix],
                record=False,
                runs=1,
                show=False,
                solution_index=int(f.name[len(prefix):-len(f.suffix)]),
            )
            if result == ExitCodes.EXIT_OK:
                console.print(f'[success]Successfully evaluated migrated {f.name} solution.[/success]')
                if not keep_backup:
                    backup_file.unlink()
                    console.print(f'[success]Deleted backup file {backup_file.name}.[/success]')
            else:
                console.print(f'[error]Failed to evaluate migrated {f.name} solution.[/error]')
                if revert_on_failure:
                    _revert(f, backup_file, keep_backup=keep_backup)
                rc = ExitCodes.EXIT_ERROR
        else:
            console.print(f'[error]Failed to migrate {f.name} to runner framework.[/error]')
            if revert_on_failure:
                _revert(f, backup_file, keep_backup=keep_backup)
            rc = ExitCodes.EXIT_ERROR
    return rc
