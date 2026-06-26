#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Transparent git clean/smudge encryption for tracked solution files.

A git *filter* must be **deterministic** -- the same plaintext has to clean to byte-identical
ciphertext every time, or git reports spurious modifications on every `status`/`add`. The crypto
core that provides this (one fixed key from a master key via HKDF, a content-derived nonce
`HMAC(plaintext)` -- the convergent-encryption trick `git-crypt` uses) lives in
`solver.crypto.ciphers`; this module is purely the git plumbing on top of it. Multi-user access comes
for free because the master key is wrapped per user (see `solver.crypto.keys`).

Wire format of an encrypted blob::

    MAGIC (5 bytes) | nonce (12 bytes) | AES-256-GCM ciphertext+tag

Filtering runs in two modes (both pass through content without MAGIC, so plaintext predating the
filter and already-encrypted blobs are never double-processed):
- `process` -- git's long-running filter protocol (pkt-line over stdin/stdout). One process handles
  every file; the master key is unwrapped and the AES cipher built exactly once. This is the high
  throughput path and what `install` wires up.
- `clean` / `smudge` -- one process per file. A fallback for direct/manual use.

Import-time contract: this module imports only `solver.crypto.ciphers`, which emits **nothing on
stdout when imported** -- in every filter mode stdout is the pkt-line / file-content channel, so a
single stray byte written during import would corrupt every blob. Keep that property when editing
either module (verified: `python -c "import solver.crypto.gitfilter"` writes 0 bytes to stdout).

The master key lives in `keys/enc-key.json` (managed by `solver.crypto.keys`); run `install` to
register the filter in the local git config and `.gitattributes`; `status` reports the wiring.
"""
from __future__ import annotations

__all__ = ['main']

import sys
from subprocess import run
from typing import BinaryIO

from cryptography.exceptions import InvalidTag

# Top-level import is safe only because importing solver.crypto.ciphers emits nothing on stdout --
# see the import-time contract in this module's docstring.
from solver.crypto.ciphers import (build_cipher, config_dict, decrypt_blob, decrypt_blob_with, encrypt_blob,
                                   encrypt_blob_with, read_master_key)

_KEY_ERRORS = (FileNotFoundError, KeyError, ValueError, InvalidTag)


# ==================================================================================================================== #
#                                               pkt-line protocol (process filter)
# ==================================================================================================================== #
def _read_exactly(src: BinaryIO, n: int) -> bytes:
    """Read exactly n bytes from src, short only at end of stream."""
    chunks: list[bytes] = []
    remaining: int = n
    while remaining:
        chunk: bytes = src.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def _read_pkt(src: BinaryIO) -> bytes | None:
    """Read one pkt-line: payload bytes, or None for a flush packet. Raises EOFError at end of stream."""
    header: bytes = _read_exactly(src, 4)
    if header == b'':
        raise EOFError
    size: int = int(header, 16)
    if size == 0:
        return None  # flush packet
    return _read_exactly(src, size - 4)


def _read_text_pkts(src: BinaryIO) -> list[str]:
    """Read text pkt-lines up to the next flush, stripping the trailing newline of each."""
    lines: list[str] = []
    while (pkt := _read_pkt(src)) is not None:
        lines.append(pkt.decode().rstrip('\n'))
    return lines


def _read_content(src: BinaryIO) -> bytes:
    """Read binary content pkt-lines up to the next flush and concatenate them."""
    chunks: list[bytes] = []
    while (pkt := _read_pkt(src)) is not None:
        chunks.append(pkt)
    return b''.join(chunks)


def _write_pkt(dst: BinaryIO, payload: bytes) -> None:
    """Write one pkt-line (4-byte hex length prefix + payload)."""
    dst.write(b'%04x' % (len(payload) + 4) + payload)


def _write_text_pkt(dst: BinaryIO, text: str) -> None:
    """Write a text pkt-line with the conventional trailing newline."""
    _write_pkt(dst, text.encode() + b'\n')


def _write_response(dst: BinaryIO, content: bytes) -> None:
    """Write a success response: status, then the content chunked into pkt-lines, then end markers."""
    _write_text_pkt(dst, 'status=success')
    dst.write(b'0000')  # flush after status
    for i in range(0, len(content), config_dict['pkt_max']):
        _write_pkt(dst, content[i:i + config_dict['pkt_max']])
    dst.write(b'0000')  # flush: end of content
    dst.write(b'0000')  # flush: empty trailing status list -> overall success
    dst.flush()


def _process() -> int:
    """Serve git's long-running filter protocol: handshake, then clean/smudge every file in one process.

    stdout is the pkt-line channel for the whole lifetime, so it is pointed at stderr; the protocol is
    driven through the captured raw buffer instead. The master key is unwrapped and the AES cipher
    built once, which is the throughput win over the per-file `clean`/`smudge` path.
    """
    src: BinaryIO = sys.stdin.buffer
    real_stdout = sys.stdout
    dst: BinaryIO = real_stdout.buffer
    sys.stdout = sys.stderr
    try:
        try:
            master_key: bytes = read_master_key()
        except _KEY_ERRORS as exc:
            print(f'gitfilter: cannot load master key: {exc}', file=sys.stderr)
            return 1
        cipher, mac_key = build_cipher(master_key)

        _read_text_pkts(src)  # client intro: git-filter-client, version=2
        _write_text_pkt(dst, 'git-filter-server')
        _write_text_pkt(dst, 'version=2')
        dst.write(b'0000')
        dst.flush()  # flush the welcome before blocking on git's reply (else deadlock)
        _read_text_pkts(src)  # advertised capabilities
        _write_text_pkt(dst, 'capability=clean')
        _write_text_pkt(dst, 'capability=smudge')
        dst.write(b'0000')
        dst.flush()

        while True:
            try:
                meta: list[str] = _read_text_pkts(src)
            except EOFError:
                return 0  # git closed the pipe: clean shutdown
            command: str = next((m.removeprefix('command=') for m in meta if m.startswith('command=')), '')
            content: bytes = _read_content(src)
            out: bytes = (encrypt_blob_with(content, cipher, mac_key) if command == 'clean'
                          else decrypt_blob_with(content, cipher))
            _write_response(dst, out)
    finally:
        sys.stdout = real_stdout


def _filter(action: str) -> int:
    """Single-file fallback: transform stdin -> stdout for one `clean` or `smudge` invocation.

    stdout carries the file content and nothing else, so key retrieval runs with stdout pointed at
    stderr; a stray line from that path would corrupt the blob.
    """
    data: bytes = sys.stdin.buffer.read()
    real_stdout = sys.stdout
    dst: BinaryIO = real_stdout.buffer
    sys.stdout = sys.stderr
    try:
        try:
            master_key: bytes = read_master_key()
        except _KEY_ERRORS as exc:
            print(f'gitfilter: cannot load master key: {exc}', file=sys.stderr)
            return 1
        out: bytes = encrypt_blob(data, master_key) if action == 'clean' else decrypt_blob(data, master_key)
    finally:
        sys.stdout = real_stdout
    dst.write(out)
    dst.flush()
    return 0


# ==================================================================================================================== #
#                                               install / status
# ==================================================================================================================== #
def _install() -> int:
    """Verify the master key first, then register the filter in git config and ensure the
    .gitattributes rule exists.

    The key check runs **before** anything is wired so a failed install never leaves the filter
    registered with `required = true` -- which would abort every later git operation on the private
    tree (checkout/status/add/commit) for a user who cannot load the key.
    """
    try:
        read_master_key()
    except _KEY_ERRORS as exc:
        print(f'gitfilter: master key check FAILED: {exc}', file=sys.stderr)
        print('gitfilter: run `solver user` and gain key access before installing; nothing was wired.', file=sys.stderr)
        return 1
    print('gitfilter: master key verified against the stored ciphertext.', file=sys.stderr)

    name: str = config_dict['filter_name']
    root = config_dict['root_dir']
    base: str = f'{sys.executable} -m solver.crypto.gitfilter'
    settings: dict[str, str] = {
        f'filter.{name}.process': f'{base} process',
        f'filter.{name}.clean': f'{base} clean',
        f'filter.{name}.smudge': f'{base} smudge',
        f'filter.{name}.required': 'true',
    }
    for key, value in settings.items():
        run(['git', 'config', '--local', key, value], cwd=root, check=True)
        print(f'git config {key} = {value}', file=sys.stderr)

    attrs_path = root / '.gitattributes'
    attr_line: str = config_dict['attr_line']
    existing: str = attrs_path.read_text() if attrs_path.exists() else ''
    if attr_line not in existing.splitlines():
        header = '' if existing.endswith('\n') or not existing else '\n'
        block = '# Transparent encryption for private solutions (solver.crypto.gitfilter).\n'
        attrs_path.write_text(f'{existing}{header}{block}{attr_line}\n')
        print(f'added rule to {attrs_path}', file=sys.stderr)
    else:
        print(f'{attrs_path} already has the rule', file=sys.stderr)
    return 0


def _status() -> int:
    """Print whether the filter is wired up in git config / .gitattributes and the master key is valid."""
    name: str = config_dict['filter_name']
    root = config_dict['root_dir']
    for action in ('process', 'clean', 'smudge', 'required'):
        result = run(['git', 'config', '--local', '--get', f'filter.{name}.{action}'],
                     cwd=root, capture_output=True, text=True)
        print(f'filter.{name}.{action} = {result.stdout.strip() or "(unset)"}', file=sys.stderr)
    attrs_path = root / '.gitattributes'
    has_rule: bool = attrs_path.exists() and config_dict['attr_line'] in attrs_path.read_text().splitlines()
    print(f'.gitattributes rule present: {has_rule}', file=sys.stderr)
    try:
        read_master_key()
        print('master key: present and verified', file=sys.stderr)
    except _KEY_ERRORS as exc:
        print(f'master key: UNAVAILABLE ({exc})', file=sys.stderr)
    return 0


# ==================================================================================================================== #
#                                               cli
# ==================================================================================================================== #
def main() -> int:
    """Dispatch a CLI action: clean | smudge | process | install | status. """
    argv = sys.argv
    actions = ('clean', 'smudge', 'process', 'install', 'status')
    if len(argv) < 2 or argv[1] not in actions:
        print(f'usage: python -m solver.crypto.gitfilter {{{"|".join(actions)}}}', file=sys.stderr)
        return 2
    action: str = argv[1]
    if action in ('clean', 'smudge'):
        return _filter(action)
    if action == 'process':
        return _process()
    if action == 'install':
        return _install()
    if action == 'status':
        return _status()
    raise AssertionError('unreachable')


if __name__ == '__main__':
    sys.exit(main())
