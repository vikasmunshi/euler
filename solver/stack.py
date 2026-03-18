#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Generator, Literal

from solver.projecteuler import init_from_projecteuler, ProjectEulerFiles, DEFAULT_FILES_SET
from solver.vault import decrypt, encrypt
from solver.workspace import BASE_DIR, MANIFEST_FILENAME, STACK_DIR, WORKSPACE_DIR

__all__ = [
    'add_file',
    'get_stack_dir',
    'stack_from_workspace',
    'unstack_to_workspace',
    'verify_manifest',
]


def add_file(stack_dir: Path, manifest: dict[str, str], filename: str, content: str) -> None:
    if (content_hash := sha256(content.encode('utf-8')).hexdigest()) != manifest.get(filename):
        filepath: Path = stack_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if is_public_problem(stack_dir):
            filepath.write_text(content)
        else:
            enc_filepath: Path = filepath.parent / (filepath.name + '.enc')
            enc_filepath.write_text(encrypt(content))
        manifest[filename] = content_hash
        write_manifest(stack_dir, manifest=manifest)
        print(f'Added {filename} to {stack_dir.relative_to(BASE_DIR).as_posix()}')


@lru_cache(maxsize=None)
def get_stack_dir(problem_number: int) -> Path:
    if not isinstance(problem_number, int) or not 1 <= problem_number <= 9999:
        raise ValueError(f'Problem number must be between 1 and 9999, got {problem_number}')
    return STACK_DIR.joinpath(*f'{problem_number:04d}')


@lru_cache(maxsize=None)
def get_problem_number(stack_dir: Path) -> int:
    parts: tuple[str, ...] = stack_dir.parts
    if len(parts) >= 5 and parts[-5] == 'stack':
        digits: str = ''.join(parts[-4:])
        return int(digits)
    raise ValueError(f'Invalid stack directory path: {stack_dir}')


@lru_cache(maxsize=None)
def is_public_problem(stack_dir: Path) -> bool:
    return get_problem_number(stack_dir) <= 100


def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    if not directory.exists():
        return None
    if directory.is_file():
        yield directory
        return None
    for path in directory.iterdir():
        if path.is_dir():
            yield from iterdir_recursive(path)
        elif path.is_file():
            yield path
    return None


def read_file(stack_dir: Path, filename: str) -> str:
    is_public: bool = is_public_problem(stack_dir)
    file_path: Path = stack_dir / filename if is_public else stack_dir / (filename + '.enc')
    if not file_path.exists():
        raise FileNotFoundError(f'File {filename} not found in stack directory')
    return file_path.read_text() if is_public else decrypt(file_path.read_text())


def read_manifest(stack_dir: Path) -> dict[str, str]:
    manifest_file: Path = stack_dir / MANIFEST_FILENAME
    if not manifest_file.exists():
        return {}
    return {filename: content_hash
            for line in manifest_file.read_text().splitlines()
            if line.strip()
            for content_hash, filename in [line.split(' ', 1)]
            if content_hash and filename}


def stack_from_workspace() -> None:
    try:
        problem_number: int = int(ProjectEulerFiles.problem_number_file.path.read_text().strip())
    except FileNotFoundError:
        print('No problem number file found in the workspace')
        return
    except ValueError:
        print('Invalid problem number in the workspace')
        return
    stack_dir: Path = get_stack_dir(problem_number)
    manifest: dict[str, str] = read_manifest(stack_dir)
    for filepath in iterdir_recursive(WORKSPACE_DIR):
        if filepath.relative_to(WORKSPACE_DIR).as_posix().split('/')[0] not in DEFAULT_FILES_SET:
            add_file(stack_dir, manifest, filepath.relative_to(WORKSPACE_DIR).as_posix(), filepath.read_text())
    return


def unstack_to_workspace(problem_number: int) -> None:
    init_from_projecteuler(problem_number)
    stack_dir: Path = get_stack_dir(problem_number)
    if stack_dir.exists():
        verify_manifest(stack_dir, verbose=True)
        manifest = read_manifest(stack_dir)
        for filename, file_hash in manifest.items():
            content: str = read_file(stack_dir, filename)
            target_file = WORKSPACE_DIR / filename
            target_file.write_text(content)
            print(f'Copied {filename} to {target_file}')


def verify_manifest(stack_dir: Path, verbose: bool = False) -> dict[str, list[str]]:
    manifest = read_manifest(stack_dir)
    results: dict[str, list[str]] = {
        'corrupted': [],
        'valid': [],
        'modified': [],
        'missing': [],
        'untracked': []
    }

    def add_to_results(category: Literal['corrupted', 'valid', 'modified', 'missing', 'untracked'], name: str) -> None:
        results[category].append(name)
        if verbose:
            print(f'file {(stack_dir / name).as_posix()} is {category}')

    for filename, expected_hash in manifest.items():
        file_path = stack_dir / filename if is_public_problem(stack_dir) else stack_dir / (filename + '.enc')
        if not file_path.exists():
            add_to_results('missing', filename)
        else:
            try:
                content = file_path.read_text() if is_public_problem(stack_dir) else decrypt(file_path.read_text())
            except (ValueError, UnicodeDecodeError) as e:
                add_to_results('corrupted', filename)
                print(f'Error reading {filename}: {e}')
            else:
                actual_hash = sha256(content.encode('utf-8')).hexdigest()
                add_to_results('valid' if actual_hash == expected_hash else 'modified', filename)
    for file_path in iterdir_recursive(stack_dir):
        if file_path.name == MANIFEST_FILENAME:
            continue
        filename = file_path.relative_to(stack_dir).as_posix()
        if filename.endswith('.enc'):
            filename = filename[:-4]
        if filename not in manifest:
            add_to_results('untracked', filename)
    return results


def write_manifest(stack_dir: Path, manifest: dict[str, str] | None = None) -> None:
    if manifest is None:
        manifest = {}
        is_public = is_public_problem(stack_dir)
        for file in iterdir_recursive(stack_dir):
            if file.name == MANIFEST_FILENAME:
                continue
            filename = file.relative_to(stack_dir).as_posix()
            if not is_public and filename.endswith('.enc'):
                filename = filename[:-4]
                content = decrypt(file.read_text())
            else:
                content = file.read_text()
            manifest[filename] = sha256(content.encode('utf-8')).hexdigest()
    manifest_file = stack_dir / MANIFEST_FILENAME
    manifest_file.write_text('\n'.join(f'{v} {k}' for k, v in manifest.items()))
