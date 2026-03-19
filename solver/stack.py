#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Generator

from solver.projecteuler import init_from_projecteuler, ProjectEulerFiles, PROBLEMS
from solver.vault import decrypt, encrypt
from solver.workspace import MANIFEST_FILENAME, STACK_DIR, WORKSPACE_DIR, iterdir_recursive

__all__ = ['Stack']


class Stack:
    __slots__ = ('__has_changes', '__manifest', '__manifest_file', 'problem_number', 'stack_dir', 'is_public',)

    def __init__(self, problem_number: int) -> None:
        if not isinstance(problem_number, int) or not PROBLEMS[0] <= problem_number <= PROBLEMS[-1]:
            raise ValueError(f'Problem number must be between {PROBLEMS[0]} and {PROBLEMS[-1]}, got {problem_number}')
        self.is_public: bool = problem_number <= 100
        self.stack_dir: Path = STACK_DIR.joinpath(*f'{problem_number:04d}')
        self.problem_number: int = problem_number
        self.__manifest_file: Path = self.stack_dir / MANIFEST_FILENAME
        self.__manifest: dict[str, str] = {}
        self.__has_changes: bool = False
        self.reload()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def __getitem__(self, key: str) -> str | None:
        return self.__manifest.get(key, None)

    def __setitem__(self, key: str, value: str) -> None:
        self.__manifest[key] = value
        self.__has_changes = True

    def __delitem__(self, key: str) -> None:
        try:
            del self.__manifest[key]
        except KeyError:
            pass
        else:
            self.__has_changes = True

    def add_file(self, filename: str, content: str) -> None:
        if (content_hash := sha256(content.encode('utf-8')).hexdigest()) == self[filename]:
            print(f'Skipped {filename} (no changes in content)')
            return
        is_public, stackpath = self.stackpath(filename)
        stackpath.parent.mkdir(parents=True, exist_ok=True)
        stackpath.write_text(content if is_public else encrypt(content))
        self[filename] = content_hash
        print(f'Added {"un" if is_public else ""}encrypted file {filename} to stack and manifest')

    def del_file(self, filename: str) -> None:
        if filename in self.__manifest:
            is_public, stackpath = self.stackpath(filename)
            stackpath.unlink(missing_ok=True)
            del self[filename]
            try:
                stackpath.parent.rmdir()
            except OSError:
                pass
            print(f'Deleted {"un" if is_public else ""}encrypted file {filename} from stack and manifest')

    def get_file(self, filename: str) -> str | None:
        is_public, stackpath = self.stackpath(filename)
        if not stackpath.exists():
            print(f'Warning: {"un" if is_public else ""}encrypted file {filename} not found in stack directory')
            return None
        return stackpath.read_text() if is_public else decrypt(stackpath.read_text())

    def get_all_files(self) -> Generator[tuple[str, str], None, None]:
        for filename, content_hash in self.__manifest.items():
            if content := self.get_file(filename):
                yield filename, content

    def list_filenames(self) -> list[str]:
        return list(self.__manifest.keys())

    def reload(self) -> None:
        if not self.__manifest_file.exists():
            self.__manifest_file.parent.mkdir(parents=True, exist_ok=True)
            self.__manifest_file.touch()
        for line in self.__manifest_file.read_text().splitlines():
            if not line:
                continue
            content_hash, filename = line.split(' ', 1)
            if filename not in self.__manifest:
                self.__manifest[filename] = content_hash

    def save(self) -> None:
        if self.__has_changes:
            self.__manifest_file.write_text('\n'.join(f'{v} {k}' for k, v in self.__manifest.items()))
            self.__has_changes = False
            print('Manifest updated')

    def stackpath(self, filename: str) -> tuple[bool, Path]:
        if self.is_public or filename.split('/')[0] in ProjectEulerFiles:
            return True, self.stack_dir / filename
        return False, self.stack_dir / (filename + '.enc')

    def verify(self) -> dict[str, list[str]]:
        results: dict[str, list[str]] = {
            'corrupted': [],
            'valid': [],
            'modified': [],
            'missing': [],
            'untracked': []
        }
        for filename, expected_hash in self.__manifest.items():
            is_public, stackpath = self.stackpath(filename)
            if not stackpath.exists():
                results['missing'].append(filename)
            else:
                try:
                    content: str = stackpath.read_text() if is_public else decrypt(stackpath.read_text())
                except (ValueError, UnicodeDecodeError):
                    results['corrupted'].append(filename)
                else:
                    actual_hash = sha256(content.encode('utf-8')).hexdigest()
                    if actual_hash == expected_hash:
                        results['valid'].append(filename)
                    else:
                        results['modified'].append(filename)
        for file_path in iterdir_recursive(self.stack_dir):
            if file_path.name == MANIFEST_FILENAME:
                continue
            filename = file_path.relative_to(self.stack_dir).as_posix()
            if filename.endswith('.enc'):
                filename = filename[:-4]
            if filename not in self.__manifest:
                results['untracked'].append(filename)
        return results

    def unstack_to_workspace(self, force_refresh: bool = False) -> None:
        print(f'Unstacking problem {self.problem_number} to workspace')
        for filename, content in self.get_all_files():
            target_file = WORKSPACE_DIR / filename
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content)
            print(f'\tCopied {filename} to {target_file}')
        for filename in ProjectEulerFiles:
            if filename == ProjectEulerFiles.problem_resources_dir:
                continue
            filepath = WORKSPACE_DIR / filename.value
            if force_refresh or not filepath.exists():
                init_from_projecteuler(self.problem_number, force_refresh=force_refresh)
        print('Unstacking complete')

    def update_stack_from_workspace(self, process_deletions: bool = False) -> None:
        print(f'Stacking workspace files to stack for problem {self.problem_number}...')
        files: set[str] = set()
        with self:
            for filepath in iterdir_recursive(WORKSPACE_DIR):
                filename: str = filepath.relative_to(WORKSPACE_DIR).as_posix()
                self.add_file(filename, filepath.read_text())
                files.add(filename)
            if process_deletions:
                for filename in self.list_filenames():
                    if filename not in files:
                        self.del_file(filename)
        print('Stacking complete')
