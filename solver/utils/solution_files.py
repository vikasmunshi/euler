#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import functools
import json
import os
from pathlib import Path

import autoflake
import black
import isort

from solver.core.config import config
from solver.core.console import console, register
from solver.core.lock import check_workspace_lock
from solver.core.problems import Problem
from solver.core.stack import read_stack_file, stack_base_dir, write_stack_file
from solver.core.templates import Templates, get_template
from solver.utils.path_utils import write_file
from solver.utils.shell_utils import run_command


@functools.lru_cache(maxsize=None)
def get_new_stuff() -> tuple[ast.FunctionDef, ast.FunctionDef, list[ast.Import | ast.ImportFrom]]:
    """ return the functions main and get_text_file and the imports from the template """
    content = get_template(Templates.NEW_PY).substitute(problem='Problem').encode()
    tree = ast.parse(content)
    imports: list[ast.Import | ast.ImportFrom] = []
    get_text_file_func: ast.FunctionDef | None = None
    main_func: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            continue
        if isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
            imports.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == 'get_text_file':
            get_text_file_func = node
        elif isinstance(node, ast.FunctionDef) and node.name == 'main':
            main_func = node
    if get_text_file_func is None:
        raise ValueError('get_text_file function not found in template')
    if main_func is None:
        raise ValueError('main function not found in template')
    return main_func, get_text_file_func, imports


def migrate_content(content: bytes) -> bytes:
    header, code = content.decode().split('from __future__ import annotations\n', 1)
    tree = ast.parse(code)
    main_func, get_text_file_func, imports = get_new_stuff()
    target_nodes: list[ast.stmt] = []
    seen_imports: set[str] = set()
    for import_line in imports:
        target_nodes.append(import_line)
        seen_imports.add(ast.unparse(import_line))
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('solver.'):
            continue  # drop from solver imports
        elif isinstance(node, ast.FunctionDef) and node.name == 'main':
            continue  # drop any existing main function (will be added from template)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if (key := ast.unparse(node)) in seen_imports:
                continue
            target_nodes.append(node)
            seen_imports.add(key)
        elif isinstance(node, ast.FunctionDef) and node.name == 'solve':
            # Remove @runner decorator from solve function
            node.decorator_list = [d for d in node.decorator_list if not (isinstance(d, ast.Name) and d.id == 'runner')]
            target_nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == 'get_text_file':
            # Replace get_text_file with the function from the template
            target_nodes.append(get_text_file_func)
        elif (
                isinstance(node, ast.If) and
                isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == '__name__' and
                len(node.test.ops) == 1 and
                isinstance(node.test.ops[0], ast.Eq) and
                len(node.test.comparators) == 1 and
                isinstance(node.test.comparators[0], ast.Constant) and
                node.test.comparators[0].value == '__main__'
        ):
            # Check if this is the if main block and replace it with main function and new if main block
            target_nodes.append(main_func)
            current_if_main = ast.unparse(node)
            updated_if_main = current_if_main.replace('(solve(', '(main(').replace('sys.argv', 'argv')
            target_nodes.append(ast.parse(updated_if_main).body[0])
        else:
            target_nodes.append(node)

    tree.body = [node for node in target_nodes]
    modified_code: str = ast.unparse(tree)
    modified_code = autoflake.fix_code(modified_code, remove_all_unused_imports=True, remove_duplicate_keys=True)
    modified_code = isort.code(modified_code, profile='black')
    modified_code = black.format_str(modified_code, mode=black.Mode(line_length=120))
    modified_code = header + 'from __future__ import annotations\n\n' + modified_code
    return modified_code.encode()


@register(name='migrate',
          help='Migrate Python solutions in the current workspace to the current template.',
          usage='migrate', )
@check_workspace_lock
def migrate_py_to_template() -> None:
    """ Migrate Python solutions in the current workspace to the new solution template structure. """
    if (problem := Problem.from_workspace()) is None:
        raise ValueError('Workspace is empty / invalid, use solver init <problem number> to initialize')
    stack_dir: Path = stack_base_dir(problem.number)
    for stack_file in stack_dir.iterdir():
        filename: str = stack_file.name.removesuffix('.enc')
        if filename.endswith('.py'):
            content, is_executable, m_time = read_stack_file(problem.number, filename)
            content = migrate_content(content)
            write_stack_file(problem.number, filename, content, is_executable, m_time)
            write_file(config.workspace_dir / filename, content, 'migrated solution file to template')


@register(name='new',
          help='Generate a new solution file for the problem in the current workspace.',
          usage='new [py_only=true]', )
@check_workspace_lock
def new_solution_files(py_only: bool = True) -> None:
    """Generate a new solution file for the problem in the given workspace.

    The new file is named based on the problem's base filename and the number of existing
    Python solution files in the workspace (e.g., "p0001_s0.py", "p0001_s1.py").

    Prompts the user for confirmation before creating the file. The file is created from
    the boilerplate template with the problem information substituted.
    """
    if (problem := Problem.from_workspace()) is None:
        raise ValueError('Workspace is empty / invalid, use solver init <problem number> to initialize')
    num_existing: int = sum(1 for s in config.workspace_dir.iterdir() if s.is_file() and s.suffix == '.py')
    names: list[str] = [f'p{problem.number:04d}_s{num_existing}.py']
    templates: list[Templates] = [Templates.NEW_PY]
    if not py_only:
        names.append(f'p{problem.number:04d}_s{num_existing}.c')
        templates.append(Templates.NEW_C)
    for name, template in zip(names, templates):
        file: Path = config.workspace_dir / name
        code: str = get_template(template).substitute(problem=problem.as_title())
        write_file(file, code.encode(), 'created solution file from template')
        if template == Templates.NEW_PY:
            os.chmod(file, 0o755)
    if not (test_cases_file := config.workspace_dir / config.test_cases_filename).exists():
        write_file(test_cases_file, b'[]', 'created empty test case file')


@register(name='recover',
          help='Recover test cases for the problem currently in the workspace.',
          usage='recover', )
@check_workspace_lock
def recover_test_cases() -> bool | None:
    """Recover test cases for the problem currently in the workspace."""
    from_revision: str = '09f3cb3de177fe19ee5262946254ddc02e0059a6'
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]No workspace initialized. Use [accent]init[/accent] to initialize the workspace[/muted]')
        return None
    test_cases_file = config.workspace_dir / config.test_cases_filename
    if test_cases_file.exists():
        console.print(f'[muted]'
                      f'Test cases for problem [accent]{problem.number}[/accent] already exist in the workspace'
                      f'[/muted]')
        return None
    console.print(f'[primary]'
                  f'Restoring test cases for problem [accent]{problem.number}[/accent] from git revision '
                  f'[muted]{from_revision}[/muted]...'
                  f'[/primary]')
    file_name: str = f'p{problem.number:04d}.py'
    # Check if file exists in the revision
    file_path = run_command(f'git ls-tree -r --name-only {from_revision} | grep -F {file_name}')
    if file_path is None:
        return None
    # Retrieve file content from the revision
    content = run_command(f'git show {from_revision}:{file_path}')
    if content is None:
        return None
    # Parse the content as Python code using AST
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
    # Find and extract the test_cases assignment
    test_cases: list[dict] | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == 'test_cases' and node.value is not None:
                try:
                    test_cases = ast.literal_eval(node.value)
                    break
                except (ValueError, SyntaxError):
                    return False
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'test_cases':
                    try:
                        test_cases = ast.literal_eval(node.value)
                        break
                    except (ValueError, SyntaxError):
                        return False
    # Write the test cases to the workspace
    write_file(config.workspace_dir / config.test_cases_filename,
               json.dumps(test_cases, indent=2).encode(),
               f'Restored test cases from git revision {from_revision}')
    return True


__all__ = ('migrate_py_to_template', 'new_solution_files', 'recover_test_cases')
