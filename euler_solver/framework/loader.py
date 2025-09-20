#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution Module loader for Project Euler problems."""
from __future__ import annotations

from base64 import b64decode, b64encode
from functools import lru_cache
from hashlib import sha256
from importlib import import_module
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_loader
from os import getenv
from pathlib import Path
from re import DOTALL, MULTILINE, Pattern, compile
from subprocess import SubprocessError, run
from sys import modules
from textwrap import fill
from types import ModuleType
from typing import cast

import Crypto  # pip install pycryptodome
import Crypto.Cipher.AES
import Crypto.Hash.SHA256
import Crypto.Util.Padding

from euler_solver.framework.file_lock import FileLock
from euler_solver.framework.logger import logger
from euler_solver.framework.paths import MAX_SHARABLE, get_c_lib_path, get_c_src_path, get_module_fqdn, get_module_path
from euler_solver.framework.register import TestCase

answer_re: Pattern[str] = compile(r"'answer': [^}]*", DOTALL | MULTILINE)
docstring_re: Pattern[str] = compile(r'(""".*?)Solution Approach', DOTALL | MULTILINE)
encrypted_re: Pattern[str] = compile(r'encrypted: str = \(([^)]*)', MULTILINE | DOTALL)
test_case_re: Pattern[str] = compile(r'^test_cases: list\[dict\[str, Any]] = \[.*\n]\n', MULTILINE | DOTALL)


@lru_cache()
def get_key() -> bytes:
    key: str | None = getenv('EULER_ENCRYPTION_KEY')
    if not key:
        raise RuntimeError('Missing EULER_ENCRYPTION_KEY in os.environ')
    return sha256(key.encode()).digest()


def encrypt(plain_text: str, *, key: bytes) -> str:
    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC)
    cipher_text = cipher.encrypt(Crypto.Util.Padding.pad(plain_text.encode(), Crypto.Cipher.AES.block_size))
    return b64encode(cast(bytes, cipher.iv) + cipher_text).decode()


def decrypt(cypher_text: str, *, key: bytes) -> str:
    try:
        cypher_text_bytes = b64decode(cypher_text)
        iv = cypher_text_bytes[:Crypto.Cipher.AES.block_size]
        cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv=iv)
        return Crypto.Util.Padding.unpad(cipher.decrypt(cypher_text_bytes[Crypto.Cipher.AES.block_size:]),
                                         Crypto.Cipher.AES.block_size).decode()
    except Exception as err:
        logger.error(f'Decryption failed: {err}')
        raise ValueError('Decryption error: Invalid key or corrupted ciphertext.') from err


def lock_private_files(euler_problem: int) -> None:
    if euler_problem <= MAX_SHARABLE:
        return
    lock_c_file(euler_problem)
    py_file_path: Path = get_module_path(euler_problem)
    if not py_file_path.exists():
        return
    with FileLock(py_file_path, 'read') as f:
        source_code: str = f.read()
    if encrypted_re.search(source_code):
        return
    tab: str = ' ' * 4
    encrypted: str = "'" + f"'\n{tab}'".join(fill(encrypt(source_code, key=get_key()), width=80).splitlines()) + "'"
    with FileLock(py_file_path, 'write') as f:
        f.write(
                '#!/usr/bin/env python3\n'
                '# -*- coding: utf-8 -*-\n'
                f'{docstring_re.search(source_code).group(1)}'  # type: ignore [union-attr]
                f'URL: https://projecteuler.net/problem={euler_problem}\n"""\n'
                'from typing import Any\n'
                f'\neuler_problem: int = {euler_problem}'
                f'\nframework_version: str = "0.0.1"\n'
                f'{answer_re.sub(r"'answer': None", test_case_re.findall(source_code)[0])}'
                f'encrypted: str = (\n{tab}{encrypted}\n)\n\n'
                "if __name__ == '__main__':\n"
                f"{tab}from euler_solver.framework import evaluate, logger\n"
                f"{tab}logger.setLevel('ERROR')\n"
                f"{tab}raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))\n"
        )


def lock_c_file(euler_problem: int) -> None:
    c_file_path: Path = get_c_src_path(euler_problem)
    if not c_file_path.exists():
        return
    with FileLock(c_file_path, 'read') as f:
        c_source_code: str = f.read()
    if 'static const char encrypted[] =' in c_source_code:
        return
    encrypted = '"' + '"\n"'.join(fill(encrypt(c_source_code, key=get_key()), width=80).splitlines()) + '"'
    with FileLock(c_file_path, 'write') as f:
        f.write(
                '/*\n'
                f' * File: {c_file_path.name}\n'
                f' * Description: C implementation for Project Euler problem {euler_problem}.\n'
                '*/\n'
                'static const char encrypted[] = {\n'
                f'{encrypted}'
                '\n};\n'
        )


def unlock_private_files(euler_problem: int) -> None:
    if euler_problem <= MAX_SHARABLE:
        return
    unlock_c_file(euler_problem)
    py_file_path: Path = get_module_path(euler_problem)
    if not py_file_path.exists():
        return
    with FileLock(py_file_path, 'read') as f:
        source_code: str = f.read()
    if not encrypted_re.search(source_code):
        return
    encrypted: str = encrypted_re.search(source_code).group(1)  # type: ignore [union-attr]
    encrypted = ''.join(line.strip().strip("'") for line in encrypted.splitlines() if line)
    decrypted: str = decrypt(encrypted, key=get_key())
    with FileLock(py_file_path, 'write') as f:
        f.write(decrypted)


def unlock_c_file(euler_problem: int) -> None:
    c_file_path: Path = get_c_src_path(euler_problem)
    if not c_file_path.exists():
        return
    with FileLock(c_file_path, 'read') as f:
        c_source_code: str = f.read()
    if 'static const char encrypted[] =' not in c_source_code:
        return
    encrypted: str = c_source_code.split('static const char encrypted[] =')[1].split('};')[0].strip().strip('"')
    decrypted: str = decrypt(encrypted, key=get_key())
    with FileLock(c_file_path, 'write') as f:
        f.write(decrypted)


def load_locked_module(euler_problem: int) -> ModuleType | None:
    module_fqdn: str = get_module_fqdn(euler_problem)
    if module_fqdn in modules:
        return modules[module_fqdn]
    if (c_file_path := get_c_src_path(euler_problem)).exists():
        make_c_lib(euler_problem, c_file_path)
    try:
        module: ModuleType = import_module(module_fqdn)
    except (ImportError, ModuleNotFoundError) as e:
        logger.error({'action': 'Module Import Failed', 'euler_problem': euler_problem, 'error': repr(e)})
        return None
    if hasattr(module, 'encrypted'):
        encrypted: str = getattr(module, 'encrypted')
        decrypted: str = decrypt(encrypted, key=get_key())
        spec: ModuleSpec = spec_from_loader(module_fqdn, loader=None)  # type: ignore [assignment]
        module = module_from_spec(spec)
        modules[module_fqdn] = module
        exec(decrypted, module.__dict__)
        setattr(module, 'module_was_encrypted', True)
    else:
        setattr(module, 'module_was_encrypted', False)
    return module


def record(euler_problem: int, test_cases: list[TestCase]) -> Path | None:
    module: ModuleType | None = load_locked_module(euler_problem)
    if module is None:
        return None
    py_file_was_locked: bool = getattr(module, 'module_was_encrypted')
    if py_file_was_locked:
        unlock_private_files(euler_problem)
    module_path: Path = get_module_path(euler_problem)
    test_cases_str: str = ('test_cases: list[dict[str, Any]] = [\n' +
                           ''.join('    {' +
                                   f"'category': '{tc.category}', "
                                   f"'input': {tc.input!r}, "
                                   f"'answer': {tc.answer!r}" +
                                   '},\n'
                                   for tc in test_cases) +
                           ']\n')
    with FileLock(module_path, 'read') as f:
        source_code: str = f.read()
    source_code = test_case_re.sub(test_cases_str, source_code)
    with FileLock(module_path, 'write') as f:
        f.write(source_code)
    if py_file_was_locked:
        lock_private_files(euler_problem)
    return module_path


def make_c_lib(euler_problem: int, c_file_path: Path, ) -> None:
    if not c_file_path.exists():
        return
    c_lib_path: Path = get_c_lib_path(euler_problem)
    if (not c_lib_path.exists()) or (c_lib_path.stat().st_mtime < c_file_path.stat().st_mtime):
        build_c_lib(c_path=c_file_path, lib_path=c_lib_path)
        c_lib_path.touch()


def build_c_lib(*, c_path: Path, lib_path: Path) -> int:
    if not c_path.exists():
        return 0
    if lib_path.exists():
        return 0
    with FileLock(c_path, 'read') as f:
        c_source_code: str = f.read()
    if 'static const char encrypted[] =' in c_source_code:
        encrypted: str = c_source_code.split('static const char encrypted[] =')[1].split('};')[0].strip().strip('"')
        decrypted: str = decrypt(encrypted, key=get_key())
    else:
        decrypted = c_source_code
    lib_dir: Path = c_path.parent
    tmp_file = c_path.with_name(f'tmp_{c_path.name}')
    o_file: str = c_path.with_suffix('.o').name
    so_file: str = lib_path.name
    c_file: str = tmp_file.name
    build_script: str = (
        '#!/usr/bin/env bash\n'
        'set -euo pipefail\n'
        f'cd {lib_dir.as_posix()}\n'
        '# Compilation flags\n'
        'CFLAGS="-Wall -Wextra -O3 -g"\n'
        'PICFLAGS="-fPIC"\n'
        '# GMP include and library paths\n'
        'GMP_INCLUDE="/usr/local/include"\n'
        'GMP_LIB="/usr/local/lib"\n'
        'LDFLAGS="-L${GMP_LIB} -lgmp"\n'
        'CPPFLAGS="-I${GMP_INCLUDE}"\n'
        f'echo "Start Build Shared Library : {c_file} -> {o_file}"\n'
        '# Compile source for shared library (without main)\n'
        'gcc ${CFLAGS} ${PICFLAGS} ${CPPFLAGS} -c ' f'"{c_file}" -o "{o_file}"\n'
        f'echo "Start Build Shared Library : {o_file} -> {so_file}"\n'
        '# Create shared library\n'
        f'gcc -shared "{o_file}" -o "{so_file}" ' '${LDFLAGS}\n'
        f'rm "{o_file}"\n'
        f'echo "Done Build Shared Library  : {c_file} -> {so_file}"\n'
    )
    try:
        with FileLock(tmp_file, 'write') as f:
            f.write(decrypted)
        result = run(build_script,
                     shell=True,
                     executable="/bin/bash",
                     capture_output=True,
                     text=True,
                     check=False)
        if result.returncode != 0:
            logger.error(f'Build failed with return code {result.returncode}')
            logger.error(f'stdout: {result.stdout}')
            logger.error(f'stderr: {result.stderr}')
            raise RuntimeError(f'Failed to build C library {so_file}')
        return result.returncode
    except SubprocessError as e:
        logger.error(f'Failed to execute build script: {e}')
        raise RuntimeError(f'Failed to build C library {so_file}: {e}')
    finally:
        tmp_file.unlink(missing_ok=True)
