#!/user/bin/env python3.14
# -*- coding: utf-8 -*-
"""AST-based migration of old euler_solver solutions into standalone Python modules."""
from __future__ import annotations

from ast import (AnnAssign, Assign, Attribute, Call, ClassDef, Expression, FunctionDef, Import, ImportFrom,
                 Name, NodeTransformer, NodeVisitor, fix_missing_locations, get_docstring, parse, unparse, walk, )
from copy import deepcopy
from json import dumps
from pathlib import Path
from shutil import rmtree
from typing import Any

from solver.config import root_dir, test_cases_filename
from solver.evaluate import evaluate
from solver.stack import stack_base_dir, write_stack_file
from solver.utils import disabled
from solver.workspace import clear_the_workspace, init_the_workspace, stack_the_workspace

_SKIP_NAMES: frozenset[str] = frozenset({'test_cases', 'euler_problem', 'framework_version'})
_FRAMEWORK_MODULE: str = 'euler_solver.framework'
_LIB_MODULE_PREFIX: str = 'euler_solver.'
_LIB_PRIMES_MODULE: str = 'euler_solver.lib_primes'

# Replacement for show_solution() that came from euler_solver.framework
_SHOW_SOLUTION_SRC: str = (
    'import sys\n'
    'def show_solution() -> bool:\n'
    "    return '--show' in sys.argv\n"
)
_SHOW_SOLUTION_NODES: list[Any] = parse(_SHOW_SOLUTION_SRC).body  # [Import, FunctionDef]

# Replacement for get_text_file() that came from euler_solver.framework
_GET_TEXT_FILE_SRC: str = (
    'from pathlib import Path\n'
    'def get_text_file(url: str) -> str:\n'
    '    """ Return the contents of a file from the \'resources\' directory. """\n'
    '    local_filename: str = \'resources\' + \'/\' + url.split("/")[-1].split("?")[0]\n'
    '    return (Path(__file__).parent / local_filename).read_text()\n'
)
_GET_TEXT_FILE_NODES: list[Any] = parse(_GET_TEXT_FILE_SRC).body  # [ImportFrom, FunctionDef]

# Replacement for pps.primes() that avoids pyprimesieve segfaults on small inputs
_GET_PRIMES_FROM_PPS_SRC: str = (
    'import bisect\n'
    'import pyprimesieve as pps\n'
    'def get_primes_from_pps(max_limit: int) -> list[int]:\n'
    '    all_primes = pps.primes(max(max_limit, 10 ** 6))\n'
    '    return all_primes[:bisect.bisect_right(all_primes, max_limit)]\n'
)
_GET_PRIMES_FROM_PPS_NODES: list[Any] = parse(_GET_PRIMES_FROM_PPS_SRC).body  # [Import, Import, FunctionDef]

# Replacement for ColorCodes that came from euler_solver.framework
_COLOR_CODES_SRC: str = (
    'from enum import StrEnum\n'
    'class ColorCodes(StrEnum):\n'
    "    GREEN = '\\033[92m'\n"
    "    YELLOW = '\\033[93m'\n"
    "    RED = '\\033[91m'\n"
    "    ORANGE = '\\033[38;5;208m'\n"
    "    BLUE = '\\033[94m'\n"
    "    CYAN = '\\033[96m'\n"
    "    MAGENTA = '\\033[95m'\n"
    "    WHITE = '\\033[97m'\n"
    "    BLACK = '\\033[30m'\n"
    "    GRAY = '\\033[90m'\n"
    "    BOLD = '\\033[1m'\n"
    "    UNDERLINE = '\\033[4m'\n"
    "    RESET = '\\033[0m'\n"
)
_COLOR_CODES_NODES: list[Any] = parse(_COLOR_CODES_SRC).body  # [ImportFrom, ClassDef]


class _ReplacePpsPrimes(NodeTransformer):
    """Replace pps.primes(x) calls with get_primes_from_pps(x)."""

    def visit_Call(self, node: Call) -> Any:
        self.generic_visit(node)
        match node.func:
            case Attribute(value=Name(id='pps'), attr='primes'):
                node.func = Name(id='get_primes_from_pps', ctx=node.func.value.ctx)  # type: ignore [attr-defined]
        return node


def _load_lib_primes_defs() -> dict[str, Any]:
    lib_file = Path(__file__).parent / 'lib_primes_pure.py'
    tree = parse(lib_file.read_text())
    return {node.name: node for node in tree.body if isinstance(node, FunctionDef)}


_LIB_PRIMES_DEFS: dict[str, Any] = _load_lib_primes_defs()


def _safe_eval(node: Any) -> Any:
    """Evaluate an AST expression node allowing literals and int(...) calls."""
    expr = fix_missing_locations(Expression(body=node))
    code = compile(expr, '<string>', 'eval')
    return eval(code, {'__builtins__': {}}, {'int': int})


def _get_source_ast_tree(problem_number: int) -> tuple[Any, str]:
    first: int = (100 * ((problem_number - 1) // 100)) + 1
    last: int = first + 99
    rel: str = (f'euler_solver/solutions/solutions_{first:04d}_{last:04d}/solution_{problem_number:04d}/'
                f'p{problem_number:04d}.py')
    return parse((root_dir / rel).read_text()), rel


def extract_test_cases(ast_tree: Any) -> list[dict[str, Any]]:
    for node in walk(ast_tree):
        match node:
            case AnnAssign(target=Name(id='test_cases'), value=value) if value is not None:
                return _safe_eval(value)  # type: ignore [no-any-return]
            case Assign(targets=[Name(id='test_cases')], value=value):
                return _safe_eval(value)  # type: ignore [no-any-return]
    raise ValueError('test_cases not found')


_FRAMEWORK_DECORATOR_NAMES: frozenset[str] = frozenset({'register_solution', 'use_c_function'})


def _is_framework_decorator(decorator: Any) -> bool:
    match decorator:
        case Name(id=name) if name in _FRAMEWORK_DECORATOR_NAMES:
            return True
        case Call(func=Name(id=name)) if name in _FRAMEWORK_DECORATOR_NAMES:
            return True
    return False


def _is_register_solution(decorator: Any) -> bool:
    match decorator:
        case Name(id='register_solution'):
            return True
        case Call(func=Name(id='register_solution')):
            return True
    return False


def _assign_name(node: Any) -> str | None:
    match node:
        case Assign(targets=[Name(id=name)]):
            return name
        case AnnAssign(target=Name(id=name)):
            return name
    return None


class _NameCollector(NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: Name) -> None:
        self.names.add(node.id)


def _names_used(node: Any) -> set[str]:
    collector = _NameCollector()
    collector.visit(node)
    return collector.names


def _collect_deps(func: FunctionDef, module_defs: dict[str, Any]) -> list[Any]:
    """Return a topologically ordered list of module-level nodes that func depends on."""
    seen: set[str] = set()
    ordered: list[Any] = []

    def visit(n: Any) -> None:
        for name in _names_used(n):
            if name in module_defs and name not in seen:
                seen.add(name)
                visit(module_defs[name])
                ordered.append(module_defs[name])

    visit(func)
    return ordered


def _filter_imports(imports: list[Any], nodes: list[Any]) -> list[Any]:
    """Keep only import aliases whose names appear in the given nodes."""
    used: set[str] = set()
    for node in nodes:
        used |= _names_used(node)

    result: list[Any] = []
    for imp in imports:
        imp_copy = deepcopy(imp)
        if isinstance(imp_copy, ImportFrom):
            imp_copy.names = [a for a in imp_copy.names if (a.asname or a.name) in used]
            if imp_copy.names:
                result.append(imp_copy)
        elif isinstance(imp_copy, Import):
            imp_copy.names = [a for a in imp_copy.names if (a.asname or a.name.split('.')[0]) in used]
            if imp_copy.names:
                result.append(imp_copy)
    return result


_SCALAR_TYPES: frozenset[str] = frozenset({'int', 'str', 'float', 'bool'})
_LITERAL_EVAL_TYPES: frozenset[str] = frozenset({'list', 'tuple', 'dict', 'List', 'Tuple', 'Dict'})


def _annotation_to_type(annotation: Any) -> str:
    """Best-effort: extract a callable type name from an annotation node."""
    match annotation:
        case Name(id=name) if name in _SCALAR_TYPES:
            return name
        case Attribute(attr=attr) if attr in _SCALAR_TYPES:
            return attr
        case Name(id=name) if name in _LITERAL_EVAL_TYPES:
            return 'literal_eval'
    return 'str'


def _has_any_recursion(node: FunctionDef) -> bool:
    """Return True if node or any nested function definition calls itself."""
    for n in walk(node):
        if isinstance(n, FunctionDef) and n.name in _names_used(n):
            return True
    return False


def _build_main_block(func: FunctionDef, *, needs_recursion_limit: bool) -> str:
    """Generate the if __name__ == '__main__': block for a solve function."""
    params = func.args.args + func.args.kwonlyargs
    call_args: list[str] = []
    needs_literal_eval: bool = False
    for i, param in enumerate(params, start=1):
        t = _annotation_to_type(param.annotation)
        if t == 'literal_eval':
            needs_literal_eval = True
        if param in func.args.kwonlyargs:
            call_args.append(f'{param.arg}={t}(sys.argv[{i}])')
        else:
            call_args.append(f'{t}(sys.argv[{i}])')
    lines: list[str] = []
    if needs_literal_eval:
        lines.append('from ast import literal_eval')
    lines.append("if __name__ == '__main__':")
    lines.append('    import sys')
    if needs_recursion_limit:
        lines.append('    sys.setrecursionlimit(10 ** 6)')
    lines.append(f'    print(solve({", ".join(call_args)}))')
    return '\n'.join(lines) + '\n'


def extract_solutions(ast_tree: Any, *, source_file: str = '') -> list[tuple[str, str]]:
    """Parse an old-style solution file and return (filename, source) for each solution."""
    _ReplacePpsPrimes().visit(ast_tree)  # pps.primes(x) → get_primes_from_pps(x) in-place
    source_docstring: str = get_docstring(ast_tree) or ''

    # Pre-populate framework replacements so _collect_deps picks them up if referenced
    module_defs: dict[str, Any] = {
        'show_solution': _SHOW_SOLUTION_NODES[1],  # [0]=Import
        'get_text_file': _GET_TEXT_FILE_NODES[1],  # [0]=ImportFrom, [1]=FunctionDef
        'get_primes_from_pps': _GET_PRIMES_FROM_PPS_NODES[2],  # [0]=Import, [1]=Import, [2]=FunctionDef
        'ColorCodes': _COLOR_CODES_NODES[1],  # [0]=ImportFrom, [1]=ClassDef
    }
    solution_funcs: list[FunctionDef] = []
    usable_imports: list[Any] = [
        _SHOW_SOLUTION_NODES[0],  # import os
        _GET_TEXT_FILE_NODES[0],  # from pathlib import Path
        _GET_PRIMES_FROM_PPS_NODES[0],  # import bisect
        _GET_PRIMES_FROM_PPS_NODES[1],  # import pyprimesieve as pps
        _COLOR_CODES_NODES[0],  # from enum import StrEnum
    ]
    has_lib_deps: bool = False

    for node in ast_tree.body:
        match node:
            case ImportFrom(module=mod) if mod == _FRAMEWORK_MODULE:
                continue  # drop euler_solver.framework entirely
            case ImportFrom(module=mod) if mod == _LIB_PRIMES_MODULE:
                module_defs.update(_LIB_PRIMES_DEFS)  # inline all; _collect_deps will prune unused
                continue
            case ImportFrom(module=mod) if mod and mod.startswith(_LIB_MODULE_PREFIX):
                has_lib_deps = True
                continue  # unknown euler_solver.lib_* — needs manual porting
            case ImportFrom() | Import():
                # skip 'from __future__ import annotations' — we add it explicitly
                if isinstance(node, ImportFrom) and node.module == '__future__':
                    continue
                usable_imports.append(node)
            case FunctionDef(name=name) if name not in _SKIP_NAMES:
                if any(_is_register_solution(d) for d in node.decorator_list):
                    solution_funcs.append(node)
                else:
                    helper = deepcopy(node)
                    helper.decorator_list = [d for d in helper.decorator_list if not _is_framework_decorator(d)]
                    module_defs[name] = helper
            case ClassDef(name=name) if name not in _SKIP_NAMES:
                module_defs[name] = node
            case _ if _assign_name(node) and _assign_name(node) not in _SKIP_NAMES:
                module_defs[_assign_name(node)] = node  # type: ignore[index]

    if has_lib_deps:
        return []  # signal caller to skip — refs functions need manual porting

    results: list[tuple[str, str]] = []
    for func in solution_funcs:
        deps = _collect_deps(func, module_defs)

        solve = deepcopy(func)
        solve.name = 'solve'
        solve.decorator_list = []

        filtered_imports = _filter_imports(usable_imports, deps + [solve])
        # primes_generator's return annotation is a string (lib_primes_pure.py uses
        # `from __future__ import annotations`), so _filter_imports cannot see Generator
        if any(isinstance(d, FunctionDef) and d.name == 'primes_generator' for d in deps):
            filtered_imports.append(parse('from typing import Generator').body[0])

        parts: list[str] = [
            '#!/usr/bin/env python3.14',
            '# -*- coding: utf-8 -*-',
            f'"""Migrated from\n    {source_file} :: {func.name}.\n\n{source_docstring}"""'.strip('\n'),
            'from __future__ import annotations',
            '',
        ]
        for imp in filtered_imports:
            parts.append(unparse(imp))
        for dep in deps:
            parts.extend(('', unparse(dep)))
        parts.extend(('', '', unparse(solve), '', ''))
        needs_recursion_limit = any(_has_any_recursion(n) for n in deps + [solve] if isinstance(n, FunctionDef))
        parts.append(_build_main_block(func, needs_recursion_limit=needs_recursion_limit))

        filename = func.name + '.py'
        results.append((filename, '\n'.join(parts)))

    return results


@disabled
def migrate_test_cases(problem_number: int) -> list[dict[str, Any]]:
    ast_tree, _ = _get_source_ast_tree(problem_number)
    try:
        test_cases: list[dict[str, Any]] = extract_test_cases(ast_tree)
    except ValueError as e:
        print(f'Error processing test cases for problem {problem_number}: {e}')
        test_cases = []
    if test_cases:
        write_stack_file(problem_number, test_cases_filename, dumps(test_cases, indent=4).encode(), is_executable=False)
    return test_cases


@disabled
def migrate_python_solutions(problem_number: int) -> int:
    print(f'Migrating {problem_number} ...')
    try:
        ast_tree, source_file = _get_source_ast_tree(problem_number)
    except FileNotFoundError:
        print(f'  Source not found for problem {problem_number}')
        return 0
    try:
        test_cases: list[dict[str, Any]] = extract_test_cases(ast_tree)
    except ValueError as e:
        print(f'  Error processing test cases, skipping {problem_number}: {e}')
        return 0
    if not test_cases:
        print(f'  No test cases, skipping {problem_number}')
        return 0
    main_tc: dict[str, Any] = next((tc for tc in test_cases if tc.get('category') == 'main'), {})
    if not main_tc:
        print(f'  No main test case, skipping {problem_number}')
        return 0
    solutions: list[tuple[str, str]] = extract_solutions(ast_tree, source_file=source_file)
    if not solutions:
        print(f'  No portable solutions (lib deps?), skipping {problem_number}')
        return 0
    write_stack_file(problem_number, test_cases_filename, dumps(test_cases, indent=4).encode(), is_executable=False)
    for name, code in solutions:
        write_stack_file(problem_number, name, code.encode(), is_executable=True)
    print(f'  Migrated {len(solutions)} solution(s) for problem {problem_number}')
    return len(solutions)


@disabled
def main() -> None:
    failed_problems: list[int] = []
    not_migrated: list[int] = []
    for n in range(1, 101):
        clear_the_workspace()
        rmtree(stack_base_dir(n), ignore_errors=True)
        init_the_workspace(n)
        stack_the_workspace()
        num = migrate_python_solutions(n)
        if num > 0:
            init_the_workspace(n)
            result = evaluate()
            if not result:
                failed_problems.append(n)
        else:
            print(f'  No solutions for problem {n}')
            not_migrated.append(n)
        clear_the_workspace()
    if failed_problems:
        print(f'Failed to migrate {len(failed_problems)} problems')
        print(f'  {failed_problems}')
    if not_migrated:
        print(f'Not migrated {len(not_migrated)} problems')
        print(f'  {not_migrated}')


if __name__ == '__main__':
    main()
