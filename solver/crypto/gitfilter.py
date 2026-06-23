#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Transparent git clean/smudge encryption for tracked solution files.

This is the deterministic counterpart to `solver.core.stack`: where the stack stores files with a
random key (drawn from the pool) and a random nonce per write, a git *filter* must be
**deterministic** -- the same plaintext has to clean to byte-identical ciphertext every time, or git
reports spurious modifications on every `status`/`add`. To get that we derive one fixed encryption
key from a dedicated master key (HKDF) and a content-derived nonce (`HMAC(plaintext)`); this is the
same convergent-encryption trick git-crypt uses. Multi-user access comes for free because the master
key is wrapped per user with the existing X25519 scheme in `solver.crypto.asymmetrical`.

The master key lives in its own file (`config.master_key_file`), wrapped to each authorised user's
public key, alongside a verification ciphertext (the master key encrypting a fixed known text) so a
loaded key can be proven correct by decrypting and comparing rather than trusted blindly.

Wire format of an encrypted blob::

    MAGIC (5 bytes) | nonce (12 bytes) | AES-256-GCM ciphertext+tag

Filtering runs in two modes (both pass through content without MAGIC, so plaintext predating the
filter and already-encrypted blobs are never double-processed):
- `process` -- git's long-running filter protocol (pkt-line over stdin/stdout). One process handles
  every file; the master key is unwrapped and the AES cipher built exactly once. This is the high
  throughput path and what `install` wires up.
- `clean` / `smudge` -- one process per file. A fallback for direct/manual use.

Import-time contract: this module imports only `solver.config` and `solver.crypto.asymmetrical`,
both of which must emit **nothing on stdout when imported** -- in every filter mode stdout is the
pkt-line / file-content channel, so a single stray byte written during import would corrupt every
blob. Keep that property when editing either module (verified: `python -c "import
solver.crypto.gitfilter"` writes 0 bytes to stdout).

Run `python -m solver.crypto.gitfilter generate-master` once to create the key, then `install` to
register the filter in the local git config and `.gitattributes`; `status` reports the wiring.
"""
from __future__ import annotations

__all__ = ['decrypt_blob', 'encrypt_blob', 'is_encrypted']

import sys
from functools import lru_cache
from hashlib import sha256
from hmac import new as hmac_new
from json import dumps, loads
from secrets import token_bytes
from subprocess import run
from typing import Any, BinaryIO, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Top-level solver.* imports are safe only because importing them emits nothing on stdout -- see the
# import-time contract in this module's docstring. Restricted to asymmetrical (UserKeyPair) + config.
from solver.config import config
from solver.crypto.asymmetrical import UserKeyPair


# Wire-format and filter constants live on `config` (config.gitfilter_*); see solver/config.py.


# ==================================================================================================================== #
#                                               deterministic encryption
# ==================================================================================================================== #
def _derive_keys(master_key: bytes) -> tuple[bytes, bytes]:
    """Derive (encryption_key, nonce_hmac_key) from the master key via HKDF-SHA256.

    Two independent 32-byte keys are derived with distinct `info` labels so the value that seeds the
    deterministic nonce can never coincide with the AES key.
    """
    enc_key: bytes = HKDF(SHA256(), 32, None, b'solver-git-filter-enc-v1').derive(master_key)
    mac_key: bytes = HKDF(SHA256(), 32, None, b'solver-git-filter-nonce-v1').derive(master_key)
    return enc_key, mac_key


def is_encrypted(blob: bytes) -> bool:
    """Return True if blob carries the filter's MAGIC header (i.e. is already ciphertext)."""
    return blob[:len(config.gitfilter_magic)] == config.gitfilter_magic


def _encrypt(plaintext: bytes, cipher: AESGCM, mac_key: bytes) -> bytes:
    """Encrypt with a prebuilt cipher: the hot-path core shared by encrypt_blob and the process loop.

    Idempotent on already-encrypted input. Nonce = `HMAC(plaintext)` so identical plaintext yields
    identical ciphertext (no spurious diffs) while distinct plaintext gets a distinct nonce, avoiding
    GCM nonce reuse under the fixed key.
    """
    if is_encrypted(plaintext):
        return plaintext
    nonce: bytes = hmac_new(mac_key, plaintext, sha256).digest()[:config.gitfilter_nonce_len]
    return config.gitfilter_magic + nonce + cipher.encrypt(nonce, plaintext, None)


def _decrypt(blob: bytes, cipher: AESGCM) -> bytes:
    """Decrypt with a prebuilt cipher; pass-through for content without MAGIC."""
    if not is_encrypted(blob):
        return blob
    return cipher.decrypt(blob[len(config.gitfilter_magic):config.gitfilter_header_len],
                          blob[config.gitfilter_header_len:], None)


def encrypt_blob(plaintext: bytes, master_key: bytes) -> bytes:
    """Encrypt plaintext deterministically for storage in git (one-shot; derives keys per call)."""
    enc_key, mac_key = _derive_keys(master_key)
    return _encrypt(plaintext, AESGCM(enc_key), mac_key)


def decrypt_blob(blob: bytes, master_key: bytes) -> bytes:
    """Decrypt a blob produced by encrypt_blob (one-shot; derives keys per call).

    Raises:
        cryptography.exceptions.InvalidTag: If the blob is corrupt or the wrong key is used.
    """
    enc_key, _ = _derive_keys(master_key)
    return _decrypt(blob, AESGCM(enc_key))


# ==================================================================================================================== #
#                                               master key file
# ==================================================================================================================== #
def _load_master_file() -> dict[str, Any]:
    """Read and parse the master-key file; raises FileNotFoundError if it has not been generated."""
    return cast(dict[str, Any], loads(config.master_key_file.read_text()))


def _write_master_file(data: dict[str, Any]) -> None:
    """Serialise the master-key file (wrapped keys + verify ciphertext)."""
    config.master_key_file.parent.mkdir(parents=True, exist_ok=True)
    config.master_key_file.write_text(dumps(data, indent=2))


def _verify(data: dict[str, Any], master_key: bytes) -> bool:
    """Return True if master_key decrypts the stored verify ciphertext back to the known plaintext."""
    try:
        return decrypt_blob(bytes.fromhex(data['verify']), master_key) == config.gitfilter_verify_text
    except (InvalidTag, ValueError, KeyError):
        return False


@lru_cache(maxsize=None)
def read_master_key() -> bytes:
    """Unlock the current user's master key from the master-key file and prove it correct.

    Returns:
        The verified 32-byte master key.

    Raises:
        FileNotFoundError: If the master-key file does not exist (run generate-master first).
        KeyError:          If the current user has no entry in the file.
        ValueError:        If the key cannot be unwrapped or fails verification against the poem.
    """
    data: dict[str, Any] = _load_master_file()
    user: UserKeyPair = UserKeyPair.from_file()
    master_key: bytes = user.unlock(data['users'][user.user_email]['master_key'])
    if not _verify(data, master_key):
        raise ValueError('master key failed verification against the stored ciphertext')
    return master_key


def _generate_master_key(force: bool) -> int:
    """Create a fresh master key, wrap it to the current user, and store it with a verify ciphertext."""
    if config.master_key_file.exists() and not force:
        print(f'gitfilter: {config.master_key_file} already exists; pass --force to overwrite', file=sys.stderr)
        return 1
    user: UserKeyPair = UserKeyPair.from_file()
    master_key: bytes = token_bytes(32)
    data: dict[str, Any] = {
        'users': {user.user_email: user.to_public_dict(master_key)},
        'verify': encrypt_blob(config.gitfilter_verify_text, master_key).hex(),
    }
    _write_master_file(data)
    print(f'gitfilter: generated master key for {user.user_email} -> {config.master_key_file}', file=sys.stderr)
    return 0


def _rekey_master_key() -> int:
    """Rotate to a new master key, re-wrap it to every authorised user, and re-encrypt tracked files.

    The current key must unwrap and verify first (proof of authority). Because the filter is
    deterministic, every committed blob depends on the master key, so rotating it requires
    re-encrypting: `git add --renormalize` re-cleans the tracked private files under the new key.
    """
    if not config.master_key_file.exists():
        print('gitfilter: no master key to rekey; run generate-master first', file=sys.stderr)
        return 1
    old: dict[str, Any] = _load_master_file()
    try:
        read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f'gitfilter: refusing to rekey -- current key check failed: {exc}', file=sys.stderr)
        return 1
    new_master: bytes = token_bytes(32)
    users: dict[str, Any] = {
        email: UserKeyPair.from_public_dict(email, cast(dict[str, str], entry)).to_public_dict(new_master)
        for email, entry in old['users'].items()
    }
    _write_master_file({'users': users, 'verify': encrypt_blob(config.gitfilter_verify_text, new_master).hex()})
    print(f'gitfilter: master key rotated for {len(users)} user(s); re-encrypting tracked files...', file=sys.stderr)
    run(['git', 'add', '--renormalize', '--', config.solutions_dir.name + '/private'],
        cwd=config.root_dir, check=False)
    print('gitfilter: done -- review `git status` and commit the re-encrypted blobs.', file=sys.stderr)
    return 0


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
    for i in range(0, len(content), config.gitfilter_pkt_max):
        _write_pkt(dst, content[i:i + config.gitfilter_pkt_max])
    dst.write(b'0000')  # flush: end of content
    dst.write(b'0000')  # flush: empty trailing status list -> overall success
    dst.flush()


def _process() -> int:
    """Serve git's long-running filter protocol: handshake, then clean/smudge every file in one process.

    stdout is the pkt-line channel for the whole lifetime, so it is pointed at stderr (the shared
    `console` writes to stdout); the protocol is driven through the captured raw buffer instead. The
    master key is unwrapped and the AES cipher built once, which is the throughput win over the
    per-file `clean`/`smudge` path.
    """
    src: BinaryIO = sys.stdin.buffer
    real_stdout = sys.stdout
    dst: BinaryIO = real_stdout.buffer
    sys.stdout = sys.stderr
    try:
        try:
            master_key: bytes = read_master_key()
        except (FileNotFoundError, KeyError, ValueError, InvalidTag) as exc:
            print(f'gitfilter: cannot load master key: {exc}', file=sys.stderr)
            return 1
        enc_key, mac_key = _derive_keys(master_key)
        cipher: AESGCM = AESGCM(enc_key)

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
            out: bytes = _encrypt(content, cipher, mac_key) if command == 'clean' else _decrypt(content, cipher)
            _write_response(dst, out)
    finally:
        sys.stdout = real_stdout


def _filter(action: str) -> int:
    """Single-file fallback: transform stdin -> stdout for one `clean` or `smudge` invocation.

    stdout carries the file content and nothing else, so key retrieval runs with stdout pointed at
    stderr (the shared `console` writes to stdout); a stray line from that path would corrupt the
    blob. The solver.* imports are top-level and output-free at import time (see module docstring).
    """
    data: bytes = sys.stdin.buffer.read()
    real_stdout = sys.stdout
    dst: BinaryIO = real_stdout.buffer
    sys.stdout = sys.stderr
    try:
        try:
            master_key: bytes = read_master_key()
        except (FileNotFoundError, KeyError, ValueError, InvalidTag) as exc:
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
    """Register the filter (process + clean/smudge fallback) in git config, ensure the .gitattributes
    rule exists, then verify the master key against the stored ciphertext or fail."""
    interpreter: str = sys.executable
    base: str = f'{interpreter} -m solver.crypto.gitfilter'
    settings: dict[str, str] = {
        f'filter.{config.gitfilter_name}.process': f'{base} process',
        f'filter.{config.gitfilter_name}.clean': f'{base} clean',
        f'filter.{config.gitfilter_name}.smudge': f'{base} smudge',
        f'filter.{config.gitfilter_name}.required': 'true',
    }
    for key, value in settings.items():
        run(['git', 'config', '--local', key, value], cwd=config.root_dir, check=True)
        print(f'git config {key} = {value}', file=sys.stderr)

    attrs_path = config.root_dir / '.gitattributes'
    existing: str = attrs_path.read_text() if attrs_path.exists() else ''
    if config.gitfilter_attr_line not in existing.splitlines():
        header = '' if existing.endswith('\n') or not existing else '\n'
        block = '# Transparent encryption for private solutions (solver.crypto.gitfilter).\n'
        attrs_path.write_text(f'{existing}{header}{block}{config.gitfilter_attr_line}\n')
        print(f'added rule to {attrs_path}', file=sys.stderr)
    else:
        print(f'{attrs_path} already has the rule', file=sys.stderr)

    try:
        read_master_key()
    except (FileNotFoundError, KeyError, ValueError, InvalidTag) as exc:
        print(f'gitfilter: master key check FAILED: {exc}', file=sys.stderr)
        print('gitfilter: run `generate-master` before using the filter.', file=sys.stderr)
        return 1
    print('gitfilter: master key verified against the stored ciphertext.', file=sys.stderr)
    return 0


def _status() -> int:
    """Print whether the filter is wired up in git config / .gitattributes and the master key is valid."""
    for action in ('process', 'clean', 'smudge', 'required'):
        result = run(['git', 'config', '--local', '--get', f'filter.{config.gitfilter_name}.{action}'],
                     cwd=config.root_dir, capture_output=True, text=True)
        print(f'filter.{config.gitfilter_name}.{action} = {result.stdout.strip() or "(unset)"}', file=sys.stderr)
    attrs_path = config.root_dir / '.gitattributes'
    has_rule: bool = attrs_path.exists() and config.gitfilter_attr_line in attrs_path.read_text().splitlines()
    print(f'.gitattributes rule present: {has_rule}', file=sys.stderr)
    try:
        read_master_key()
        print('master key: present and verified', file=sys.stderr)
    except (FileNotFoundError, KeyError, ValueError, InvalidTag) as exc:
        print(f'master key: UNAVAILABLE ({exc})', file=sys.stderr)
    return 0


# ==================================================================================================================== #
#                                               cli
# ==================================================================================================================== #
def main() -> int:
    """Dispatch a CLI action: clean | smudge | process | install | status | generate-master | rekey-master."""
    argv = sys.argv
    actions = ('clean', 'smudge', 'process', 'install', 'status', 'generate-master', 'rekey-master')
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
    if action == 'generate-master':
        return _generate_master_key('--force' in argv[2:])
    if action == 'rekey-master':
        return _rekey_master_key()
    raise AssertionError('unreachable')


if __name__ == '__main__':
    sys.exit(main())
