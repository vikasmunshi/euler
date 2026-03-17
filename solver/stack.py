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

from solver.download import download_file
from solver.vault import decrypt, encrypt

__all__ = [
    'STACK_DIR',
    'WORKSPACE_DIR',
    'add_file',
    'fill_stack',
    'get_stack_dir',
    'stack_from_workspace',
    'unstack_to_workspace',
    'verify_manifest',
]

# Type aliases for improved code clarity and type hints
StackDir: type = Path  # Path to a problem's stack directory
ProblemNumber: type = int  # Project Euler problem number (1-9999)

# Directory constants
BASE_DIR: Path = Path.cwd()  # Project root directory
STACK_DIR: Path = BASE_DIR / 'stack'  # Base stack directory
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'  # Working/temporary files directory

# Module-level constants
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'
PROBLEM_NUMBER_FILE: Path = WORKSPACE_DIR / 'problem_number.txt'
MANIFEST_FILENAME: str = 'manifest.txt'


def add_file(stack_dir: Path, manifest: dict[str, str], filename: str, content: str) -> None:
    """Add a file to the stack directory and update the manifest.

    Creates the file in the stack directory if the content hash differs from what's
    recorded in the manifest. The manifest is updated with the new content hash.

    For private problems (101+), files are automatically encrypted and saved with
    a .enc extension on disk. However, the manifest stores the original filename
    (without .enc) to maintain a clean abstraction. When unstacking, the .enc
    extension is removed automatically during decryption.

    Args:
        stack_dir: The stack directory where the file should be added.
        manifest: Dictionary mapping filenames to content_hash.
        filename: The relative filename within the stack directory (without .enc).
        content: The text content to write to the file (plaintext).

    Returns:
        None

    Note:
        - Public problems (1-100): Files stored as plaintext with original filename
        - Private problems (101+): Files encrypted and stored as filename.enc
        - Manifest always tracks the original filename (not the .enc version)
        - Content hash in the manifest is computed from plaintext, not encrypted data
    """
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


def add_resource(stack_dir: Path, manifest: dict[str, str], resource: str,
                 force_refresh: bool = False) -> None:
    """Add a resource file to the stack directory.

    Downloads a resource from Project Euler and adds it to the stack directory
    with a sanitized filename.

    Args:
        stack_dir: The stack directory where the resource should be added.
        manifest: Dictionary mapping filename to content_hash.
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
        stack_dir: Path = get_stack_dir(problem_number)
        init_from_projecteuler(problem_number, force_refresh=refresh_problems)
        manifest: dict[str, str] = read_manifest(stack_dir)
        print(f'Problem {problem_number} -> {stack_dir} ({len(manifest)} files)')


@lru_cache(maxsize=None)
def get_stack_dir(problem_number: ProblemNumber) -> StackDir:
    """Get the stack directory path for a given problem number.

    Converts a Project Euler problem number into its corresponding hierarchical
    stack directory path. The problem number is zero-padded to 4 digits, then
    each digit becomes a separate directory level in the path hierarchy.

    The function uses LRU caching with unlimited cache size to avoid repeated
    path construction for frequently accessed problem numbers.

    Path Format: stack/d1/d2/d3/d4/
        where d1, d2, d3, d4 are the individual digits of the 4-digit number

    Args:
        problem_number: The Project Euler problem number (1-9999).

    Returns:
        Path: The stack directory path for the problem, relative to STACK_DIR.

    Raises:
        ValueError: If problem_number is not in the valid range (1-9999).

    Examples:
        >>> get_stack_dir(1)
        PosixPath('solver/stack/0/0/0/1')
        >>> get_stack_dir(42)
        PosixPath('solver/stack/0/0/4/2')
        >>> get_stack_dir(123)
        PosixPath('solver/stack/0/1/2/3')
        >>> get_stack_dir(10000)
        Traceback (the most recent call last):
            ...
        ValueError: Problem number must be between 1 and 9999, got 10000

    Note:
        This function is cached. Repeated calls with the same problem_number
        will return the cached result without recomputing the path.
    """
    if not isinstance(problem_number, int) or not 1 <= problem_number <= 9999:
        raise ValueError(f'Problem number must be between 1 and 9999, got {problem_number}')
    return STACK_DIR.joinpath(*f'{problem_number:04d}')


@lru_cache(maxsize=None)
def get_problem_number(stack_dir: StackDir) -> ProblemNumber:
    """Get the problem number from a stack directory path.

    Reverse operation of get_stack_dir(). Extracts the problem number by
    parsing the hierarchical directory structure where each of the last 4
    path components represents a single digit.

    The function validates that the path has the expected structure (at least
    5 parts with 'stack' as the 5th from the end) and extracts the last
    4 parts as digits to reconstruct the problem number.

    The function uses LRU caching with unlimited cache size for performance.

    Expected Path Format: .../stack/d1/d2/d3/d4[/...]
        where d1, d2, d3, d4 are single-digit directory names

    Args:
        stack_dir: The stack directory path (Path object or path-like).

    Returns:
        int: The Project Euler problem number (1-9999).

    Raises:
        ValueError: If the path doesn't match the expected stack directory
                    format (i.e., doesn't have 'stack' as the 5th component
                    from the end, or has fewer than 5 parts).

    Examples:
        >>> get_problem_number(Path('solver/stack/0/0/0/1'))
        1
        >>> get_problem_number(Path('solver/stack/0/0/4/2'))
        42
        >>> get_problem_number(Path('solver/stack/0/1/2/3'))
        123

    Note:
        This function is cached. Repeated calls with the same stack_dir
        will return the cached result without reparsing the path.
    """
    parts: tuple[str, ...] = stack_dir.parts
    if len(parts) >= 5 and parts[-5] == 'stack':
        digits: str = ''.join(parts[-4:])
        return int(digits)
    raise ValueError(f'Invalid stack directory path: {stack_dir}')


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

    Raises:
        ValueError: If the problem HTML structure is invalid or required elements are missing.
        RuntimeError: If the download fails or a network error occurs.

    Note:
        This function expects Project Euler HTML to contain:
        - An <h2> tag with the problem title
        - A <div class="problem_content"> with the problem description
        - Optional <a> tags with href="resources/..." for resource files
    """
    stack_dir: Path = get_stack_dir(problem_number)
    stack_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = read_manifest(stack_dir)
    problem_url: str = f'{PROJECTEULER_URL}/problem={problem_number}'

    try:
        problem_html: str = download_file(problem_url, force_refresh=force_refresh)
    except Exception as e:
        raise RuntimeError(f'Failed to download problem {problem_number} from {problem_url}: {e}') from e

    problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')

    # Extract and validate problem content
    problem_content_obj: BeautifulSoup | None = problem_soup.find('div', {'class': 'problem_content'})
    if not problem_content_obj:
        raise ValueError(f'Problem {problem_number}: Could not find problem_content div in HTML')

    problem_content: str = problem_content_obj.text.strip()

    # Extract and validate problem title
    title_obj: BeautifulSoup | None = problem_soup.find('h2')
    if not title_obj:
        raise ValueError(f'Problem {problem_number}: Could not find h2 title element in HTML')

    problem_title: str = sanitize_filename(title_obj.text.strip())

    # Save problem files
    add_file(stack_dir, manifest, f'{problem_title}.html', problem_html)
    add_file(stack_dir, manifest, f'{problem_title}.md', problem_title + '\n\n' + problem_content)
    add_file(stack_dir, manifest, f'{problem_title}.url', problem_url)

    # Download resources with error handling
    for resource in (u for a in problem_content_obj.find_all('a')
                     if (u := a.get('href', '')).startswith('resources/')):
        try:
            add_resource(stack_dir, manifest, resource, force_refresh=force_refresh)
        except Exception as e:
            print(f'Warning: Failed to download resource {resource}: {e}')


@lru_cache(maxsize=None)
def is_public_problem(stack_dir: Path) -> bool:
    """Check if a problem is public on Project Euler.

    Project Euler makes the first 100 problems publicly available without
    requiring authentication. This function determines whether a problem
    should be stored in plaintext (public) or encrypted (private).

    Args:
        stack_dir: The stack directory path for the problem.

    Returns:
        bool: True if the problem number is 100 or less, False otherwise.

    Examples:
        >>> is_public_problem(get_stack_dir(1))
        True
        >>> is_public_problem(get_stack_dir(100))
        True
        >>> is_public_problem(get_stack_dir(101))
        False

    Note:
        This function is cached for performance.
    """
    return get_problem_number(stack_dir) <= 100


def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    """Recursively iterate over all files in a directory and its subdirectories.

    Performs a depth-first traversal of the directory tree, yielding Path objects
    for all files encountered. Directories are traversed recursively but not yielded.
    If the provided path is itself a file, only that file is yielded.

    Args:
        directory: The directory path to traverse, or a file path.

    Yields:
        Path: Each file found in the directory tree.

    Returns:
        None: Always returns None when the generator is exhausted.

    Examples:
        >>> list(iterdir_recursive(Path('solver/stack/0/0/0/1')))
        [PosixPath('solver/stack/0/0/0/1/manifest.txt'),
         PosixPath('solver/stack/0/0/0/1/problem.html'), ...]

    Note:
        - If the directory doesn't exist, no files are yielded
        - Hidden files and directories are included in the traversal
        - Symbolic links are followed
    """
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
    """Read a file from the stack directory.

    For public problems (1-100), reads files directly as plaintext.
    For private problems (101+), reads encrypted files (.enc) and decrypts them.

    Args:
        stack_dir: The stack directory containing the file.
        filename: The relative filename within the stack directory (without .enc extension).

    Returns:
        str: The file content as plaintext.

    Raises:
        FileNotFoundError: If the file doesn't exist in the stack directory.
    """
    is_public: bool = is_public_problem(stack_dir)
    file_path: Path = stack_dir / filename if is_public else stack_dir / (filename + '.enc')
    if not file_path.exists():
        raise FileNotFoundError(f'File {filename} not found in stack directory')
    return file_path.read_text() if is_public else decrypt(file_path.read_text())


def read_manifest(stack_dir: Path) -> dict[str, str]:
    """Load the manifest file for a given stack directory.

    Reads the manifest.txt file and parses it into a dictionary mapping filenames
    to their SHA-256 content hashes. Each line in the manifest has the format:
    '<content_hash> <filename>'.

    Args:
        stack_dir: The stack directory containing the manifest file.

    Returns:
        dict[str, str]: Dictionary mapping filenames to their SHA-256 content hashes.
                       Returns an empty dict if the manifest file doesn't exist.

    Examples:
        >>> read_manifest(Path('solver/stack/0/0/0/1'))
        {'problem.html': 'abc123...', 'problem.md': 'def456...'}

    Note:
        Empty lines and lines that cannot be properly split are silently ignored.
    """
    manifest_file: Path = stack_dir / MANIFEST_FILENAME
    if not manifest_file.exists():
        return {}
    return {filename: content_hash
            for line in manifest_file.read_text().splitlines()
            if line.strip()
            for content_hash, filename in [line.split(' ', 1)]
            if content_hash and filename}


@lru_cache(maxsize=None)
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
    reserved_names: set[str] = {'', '.', '..', 'con', 'prn', 'aux', 'nul',
                                'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
                                'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
    # Check base name without extension for reserved names
    base_name: str = filename.split('.')[0] if '.' in filename else filename
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
        problem_number: int = int(PROBLEM_NUMBER_FILE.read_text())
        stack_dir: Path = get_stack_dir(problem_number)
        manifest: dict[str, str] = read_manifest(stack_dir)
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

    Before unstacking, verifies file integrity by comparing actual file hashes
    against the manifest. Issues warnings for any modified, missing, or untracked
    files but continues with the unstacking process.

    Args:
        problem_number: The Project Euler problem number to unstack.

    Returns:
        None
    """
    if WORKSPACE_DIR.exists():
        rmtree(WORKSPACE_DIR, ignore_errors=True)
    WORKSPACE_DIR.mkdir(exist_ok=True, parents=True)
    stack_dir: Path = get_stack_dir(problem_number)
    if not stack_dir.exists():
        init_from_projecteuler(problem_number, force_refresh=False)

    # Verify manifest and warn on integrity issues
    verification_results = verify_manifest(stack_dir, verbose=False)
    if verification_results['modified']:
        print(f'Warning: Modified files detected: {", ".join(verification_results['modified'])}')
    if verification_results['missing']:
        print(f'Warning: Missing files detected: {", ".join(verification_results['missing'])}')
    if verification_results['untracked']:
        print(f'Warning: Untracked files detected: {", ".join(verification_results['untracked'])}')
    if not any([verification_results['modified'], verification_results['missing'], verification_results['untracked']]):
        print(f'All files verified successfully for problem {problem_number}')

    manifest = read_manifest(stack_dir)
    for filename, file_hash in manifest.items():
        content: str = read_file(stack_dir, filename)
        target_file = WORKSPACE_DIR / filename
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content)
        print(f'Copied {filename} to {target_file}')
    PROBLEM_NUMBER_FILE.write_text(str(problem_number))


def verify_manifest(stack_dir: Path, verbose: bool = False) -> dict[str, list[str]]:
    """Verify file integrity by comparing actual file hashes against the manifest.

    Checks all files in the stack directory against their recorded hashes in the
    manifest. Identifies files that have been modified, are missing from the disk,
    or are present but not tracked in the manifest.

    For encrypted files (.enc), the content is decrypted before hashing to match
    the plaintext hash stored in the manifest.

    Args:
        stack_dir: The stack directory to verify.
        verbose: If True, prints detailed information about each verification step.
                Defaults to False.

    Returns:
        dict[str, list[str]]: A dictionary with verification results:
            - 'valid': List of filenames that match their manifest hashes
            - 'modified': List of filenames with mismatched hashes
            - 'missing': List of filenames in manifest but not on disk
            - 'untracked': List of filenames on disk but not in manifest

    Examples:
        >>> _results = verify_manifest(get_stack_dir(1))
        >>> if results['modified']:
        ...     print(f"Modified files: {results['modified']}")
        >>> if not any(results.values()):
        ...     print("All files verified successfully")

    Note:
        - The manifest file itself is excluded from verification
        - For private problems, .enc files are decrypted before hash comparison
        - Empty result lists indicate no issues in that category
    """
    manifest = read_manifest(stack_dir)
    results = {
        'valid': [],
        'modified': [],
        'missing': [],
        'untracked': []
    }

    # Check files listed in the manifest
    for filename, expected_hash in manifest.items():
        if is_public_problem(stack_dir):
            file_path = stack_dir / filename
        else:
            file_path = stack_dir / (filename + '.enc')

        if not file_path.exists():
            results['missing'].append(filename)
            if verbose:
                print(f'Missing: {filename}')
        else:
            try:
                if is_public_problem(stack_dir):
                    content = file_path.read_text()
                else:
                    content = decrypt(file_path.read_text())

                actual_hash = sha256(content.encode('utf-8')).hexdigest()

                if actual_hash == expected_hash:
                    results['valid'].append(filename)
                    if verbose:
                        print(f'Valid: {filename}')
                else:
                    results['modified'].append(filename)
                    if verbose:
                        print(f'Modified: {filename} (expected {expected_hash[:8]}..., got {actual_hash[:8]}...)')
            except Exception as e:
                results['modified'].append(filename)
                if verbose:
                    print(f'Error verifying {filename}: {e}')

    # Check for untracked files on the disk
    for file_path in iterdir_recursive(stack_dir):
        if file_path.name == MANIFEST_FILENAME:
            continue

        filename = file_path.relative_to(stack_dir).as_posix()

        # For encrypted files, check without .enc extension
        if filename.endswith('.enc'):
            filename = filename[:-4]

        if filename not in manifest:
            results['untracked'].append(filename)
            if verbose:
                print(f'Untracked: {filename}')

    return results


def write_manifest(stack_dir: Path, manifest: dict[str, str] | None = None) -> None:
    """Update the manifest file for a given stack directory.

    Writes the manifest dictionary to manifest.txt in the format:
    '<filename_hash> <content_hash> <filename>' (one entry per line).
    If no manifest is provided, generates one by scanning all files in the stack directory
    (excluding the manifest file itself) and computing their SHA-256 hashes.

    Args:
        stack_dir: The stack directory where the manifest file should be written.
        manifest: Optional dictionary mapping filename to content_hash tuples.
                 If None, the manifest is generated from the current directory contents.
                 Defaults to None.

    Returns:
        None
    """
    if manifest is None:
        manifest = {}
        is_public = is_public_problem(stack_dir)
        for file in iterdir_recursive(stack_dir):
            if file.name == MANIFEST_FILENAME:
                continue
            filename = file.relative_to(stack_dir).as_posix()
            # Handle encrypted files
            if not is_public and filename.endswith('.enc'):
                filename = filename[:-4]
                content = decrypt(file.read_text())
            else:
                content = file.read_text()
            manifest[filename] = sha256(content.encode('utf-8')).hexdigest()
    manifest_file = stack_dir / MANIFEST_FILENAME
    manifest_file.write_text('\n'.join(f'{v} {k}' for k, v in manifest.items()))
