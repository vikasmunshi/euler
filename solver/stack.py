#!/usr/bin/env python3
"""
Stack module for managing Project Euler problem resources.

This module provides functionality for downloading, organizing, and caching Project Euler
problems and their associated resources. Each problem is stored in its own directory with
HTML, Markdown, and resource files, with a manifest tracking all downloaded files using
SHA-256 hashes for content verification.

The module uses a stack-based approach where problems are downloaded to a 'stack' directory
and can be unstacked to a 'workspace' directory for active work. Changes in the workspace
can be stacked back to update the problem files.

Directory Structure:
    stack/
        0/0/0/1/          # Problem 1
            manifest.txt  # File manifest with hashes
            *.html        # Problem HTML
            *.md          # Problem Markdown
            *.url         # Problem URL
            resources/    # Associated resources

Usage:
    # Download and organize problems
    fill_stack(problems=[1, 2, 3])

    # Work with a specific problem
    unstack_to_workspace(problem_number=1)
    # ... make changes in workspace ...
    stack_from_workspace()
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from re import sub
from shutil import rmtree
from typing import Generator

from bs4 import BeautifulSoup

from solver.cached_download import download_file

__all__ = [
    'add_file',
    'fill_stack',
    'read_manifest',
    'stack_from_workspace',
    'unstack_to_workspace',
    'write_manifest',
]

# Module-level constants
BASE_DIR: Path = Path.cwd()
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'
PROBLEM_NUMBER_FILE: Path = WORKSPACE_DIR / 'problem_number.txt'
MANIFEST_FILENAME: str = 'manifest.txt'


def add_file(stack_dir: Path, manifest: dict[str, tuple[str, str]], filename: str, content: str) -> None:
    """Add a file to the stack directory and update the manifest.

    Creates the file in the stack directory if the content hash differs from what's
    recorded in the manifest. The manifest is updated with the new content hash.

    Args:
        stack_dir: The stack directory where the file should be added.
        manifest: Dictionary mapping filename hashes to (content_hash, filename) tuples.
        filename: The relative filename within the stack directory.
        content: The text content to write to the file.

    Returns:
        None
    """
    filename_hash = sha256(filename.encode('utf-8')).hexdigest()
    content_hash = sha256(content.encode('utf-8')).hexdigest()
    if content_hash != manifest.get(filename_hash, ('', ''))[0]:
        filepath: Path = stack_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        manifest[filename_hash] = content_hash, filename
        print(f'Added {filename} to {stack_dir.relative_to(BASE_DIR).as_posix()}')


def add_resource(stack_dir: Path, manifest: dict[str, tuple[str, str]], resource: str,
                 force_refresh: bool = False) -> None:
    """Add a resource file to the stack directory.

    Downloads a resource from Project Euler and adds it to the stack directory
    with a sanitized filename.

    Args:
        stack_dir: The stack directory where the resource should be added.
        manifest: Dictionary mapping filename hashes to (content_hash, filename) tuples.
        resource: The resource path relative to projecteuler.net (e.g., 'resources/file.txt').
        force_refresh: If True, bypass the cache and re-download the resource. Defaults to False.

    Returns:
        None
    """
    filename: str = sanitize_filename(resource.split('/')[-1])
    content: str = download_file(f'{PROJECTEULER_URL}/{resource.lstrip('/')}', force_refresh=force_refresh)
    add_file(stack_dir=stack_dir, manifest=manifest, filename=f'resources/{filename}', content=content)


def fill_stack(problems: list[int] | None = None, refresh_list: bool = False, refresh_problems: bool = False) -> None:
    """Fill the stack with Project Euler problems.

    Downloads and organizes the specified problems (or all available problems if none specified)
    into their respective stack directories. Each problem's manifest is read and updated,
    and the number of files is reported.

    Args:
        problems: List of problem numbers to download. If None, downloads all available problems
                 from the Project Euler minimal problems list. Defaults to None.
        refresh_list: If True, forces a refresh of the problems list from Project Euler.
                     Defaults to False.
        refresh_problems: If True, forces a refresh of all problem content from Project Euler.
                         Defaults to False.

    Returns:
        None
    """
    if problems is None:
        problems = [int(line.split('##')[0])
                    for line in download_file(PROBLEMS_LIST_URL, force_refresh=refresh_list).strip().splitlines()[1:]]
    for problem_number in problems:
        stack_dir = get_stack_dir(problem_number)
        init_from_projecteuler(problem_number, force_refresh=refresh_problems)
        manifest: dict[str, tuple[str, str]] = read_manifest(stack_dir)
        print(f'Problem {problem_number} -> {stack_dir} ({len(manifest)} files)')


@lru_cache(maxsize=None)
def get_stack_dir(problem_number: int) -> Path:
    """Get the stack directory path for a given problem number.

    Returns a path with the format: stack/d1/d2/d3/d4/ where d1-d4 are the
    individual digits of the zero-padded 4-digit problem number.
    Results are cached for performance.

    Args:
        problem_number: The Project Euler problem number.

    Returns:
        Path: The stack directory path for the problem.

    Example:
        >>> get_stack_dir(1)
        PosixPath('stack/0/0/0/1')
        >>> get_stack_dir(123)
        PosixPath('stack/0/1/2/3')
    """
    return BASE_DIR / 'stack' / '/'.join(f'{problem_number:04d}')


def init_from_projecteuler(problem_number: int, force_refresh: bool = False) -> None:
    """Initialize a problem stack from the Project Euler website.

    Downloads the problem HTML, extracts the problem content, title, and resources,
    then saves them to the stack directory in multiple formats (HTML, Markdown, URL).
    All associated resource files are also downloaded and added to the stack.
    The manifest is updated to track all files.

    Args:
        problem_number: The Project Euler problem number to initialize.
        force_refresh: If True, bypasses cache and re-downloads all content and resources.
                      Defaults to False.

    Returns:
        None
    """
    stack_dir: Path = get_stack_dir(problem_number)
    stack_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, tuple[str, str]] = read_manifest(stack_dir)
    problem_url: str = f'{PROJECTEULER_URL}/problem={problem_number}'
    problem_html: str = download_file(problem_url, force_refresh=force_refresh)
    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
    problem_content_obj = problem_soup.find('div', {'class': 'problem_content'})
    problem_content: str = problem_content_obj.text.strip()
    problem_title: str = sanitize_filename(problem_soup.find('h2').text.strip())
    add_file(stack_dir, manifest, f'{problem_title}.html', problem_html)
    add_file(stack_dir, manifest, f'{problem_title}.md', problem_title + '\n\n' + problem_content)
    add_file(stack_dir, manifest, f'{problem_title}.url', problem_url)
    for resource in (u for a in problem_content_obj.find_all('a') if (u := a.get('href')).startswith('resources/')):
        add_resource(stack_dir, manifest, resource, force_refresh=force_refresh)
    write_manifest(stack_dir, manifest=manifest)


def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    """Recursively iterate over all files in a directory and its subdirectories."""
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


def read_manifest(stack_dir: Path) -> dict[str, tuple[str, str]]:
    """Load the manifest file for a given stack directory.

    Reads the manifest.txt file and parses it into a dictionary mapping filename hashes
    to content hashes and filenames. Each line in the manifest has the format:
    '<filename_hash> <content_hash> <filename>'.

    Args:
        stack_dir: The stack directory containing the manifest file.

    Returns:
        dict[str, tuple[str, str]]: Dictionary mapping filename hashes (SHA-256) to tuples
                                    of (content_hash, filename). Returns an empty dict if
                                    the manifest file doesn't exist.
    """
    manifest_file = stack_dir / MANIFEST_FILENAME
    if not manifest_file.exists():
        return {}
    return {filename_hash: (content_hash, filename)
            for line in manifest_file.read_text().splitlines()
            for filename_hash, content_hash, filename in (line.split(' ', 2),)
            if content_hash and filename_hash and filename}


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be POSIX-compliant and human-readable.

    Converts the filename to lowercase, removes invalid characters (NUL, path separators),
    normalizes whitespace, and handles special cases like empty names or CLI flag-like names.

    Args:
        filename: The original filename string to sanitize.

    Returns:
        str: A sanitized filename that is safe to use on POSIX filesystems.

    Example:
        >>> sanitize_filename("Problem 1: Multiples / 3 or 5")
        'problem 1: multiples - 3 or 5'
        >>> sanitize_filename("--dangerous")
        '_--dangerous'
    """
    filename = filename.lower()
    # Make it POSIX and Windows valid: forbid NUL, path separators, and Windows reserved chars
    for char in '\0/<>:"|?*\\':
        filename = filename.replace(char, '-')
    # Normalize whitespace for nicer filenames
    filename = sub(r'\s+', ' ', filename).strip()
    # Remove trailing periods and spaces (Windows restriction)
    filename = filename.rstrip('. ')
    # Avoid special/empty names and Windows reserved device names
    reserved_names = {'', '.', '..', 'con', 'prn', 'aux', 'nul',
                      'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
                      'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
    # Check base name without extension for reserved names
    base_name = filename.split('.')[0] if '.' in filename else filename
    if base_name in reserved_names:
        filename = 'no-name' if not filename or filename in {'.', '..'} else '_' + filename
    # Avoid filenames that look like CLI flags
    if filename.startswith('-'):
        filename = '_' + filename
    return filename


def stack_from_workspace() -> None:
    """Copy workspace content back to the stack and update the manifest.

    Reads the problem number from the workspace, then copies all files (except the
    manifest and problem_number.txt) from the workspace back to the corresponding
    stack directory. The stack's manifest is updated to reflect any changes.
    If no problem number file exists in the workspace, no action is taken.

    Returns:
        None
    """
    if PROBLEM_NUMBER_FILE.exists():
        problem_number = int(PROBLEM_NUMBER_FILE.read_text())
        stack_dir = get_stack_dir(problem_number)
        manifest: dict[str, tuple[str, str]] = read_manifest(stack_dir)
        for filename in iterdir_recursive(WORKSPACE_DIR):
            if filename.name not in {MANIFEST_FILENAME, PROBLEM_NUMBER_FILE.name}:
                add_file(stack_dir, manifest, filename.relative_to(WORKSPACE_DIR).as_posix(), filename.read_text())
    return None


def unstack_to_workspace(problem_number: int) -> None:
    """Unstack a problem to the workspace directory.

    Clears the workspace directory and copies all files from the specified problem's
    stack directory to the workspace. If the problem hasn't been downloaded yet,
    it will be initialized from Project Euler first. A problem_number.txt file is
    created in the workspace to track which problem is currently active.

    Args:
        problem_number: The Project Euler problem number to unstack.

    Returns:
        None
    """
    if WORKSPACE_DIR.exists():
        rmtree(WORKSPACE_DIR, ignore_errors=True)
    WORKSPACE_DIR.mkdir(exist_ok=True, parents=True)
    stack_dir = get_stack_dir(problem_number)
    if not stack_dir.exists():
        init_from_projecteuler(problem_number, force_refresh=False)
    for file in iterdir_recursive(stack_dir):
        if file.name == MANIFEST_FILENAME:
            continue
        filename: str = file.relative_to(stack_dir).as_posix()
        target_file = WORKSPACE_DIR / filename
        target_file.parent.mkdir(parents=True, exist_ok=True)
        file.copy(target_file)
        print(f'Copied {file} to {target_file}')
    PROBLEM_NUMBER_FILE.write_text(str(problem_number))


def write_manifest(stack_dir: Path, manifest: dict[str, tuple[str, str]] | None = None) -> None:
    """Update the manifest file for a given stack directory.

    Writes the manifest dictionary to manifest.txt in the format:
    '<filename_hash> <content_hash> <filename>' (one entry per line).
    If no manifest is provided, generates one by scanning all files in the stack directory
    (excluding the manifest file itself) and computing their SHA-256 hashes.

    Args:
        stack_dir: The stack directory where the manifest file should be written.
        manifest: Optional dictionary mapping filename hashes to (content_hash, filename) tuples.
                 If None, the manifest is generated from the current directory contents.
                 Defaults to None.

    Returns:
        None
    """
    if manifest is None:
        manifest = {sha256(filename.encode('utf-8')).hexdigest():
                        (sha256(file.read_text().encode('utf-8')).hexdigest(), filename)
                    for file in iterdir_recursive(stack_dir)
                    if file.name != MANIFEST_FILENAME
                    if (filename := file.relative_to(stack_dir).as_posix())}
    manifest_file = stack_dir / MANIFEST_FILENAME
    manifest_file.write_text('\n'.join(f'{k} {v[0]} {v[1]}' for k, v in manifest.items()))
