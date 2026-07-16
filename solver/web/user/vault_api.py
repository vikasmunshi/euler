#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Vault + account routes for the per-user service.

These routes only exist on the per-user instance — the process runs as the collaborator's
own uid, so ``~/.euler`` *is* their vault and acting on it needs no privilege dance.

**The web unlock path.** The browser derives ``PK`` itself (WebCrypto PBKDF2 over
the password it already holds and the SRP salt) and sends only ``PK`` here over TLS; the
service unwraps ``VK`` and materialises the uid-private tmpfs key file
(:func:`solver.crypto.vault.write_session_key`), which every later-forked shell — and the
git filter under it — inherits by path. The password never reaches any server, and the
auth service (which could never derive ``PK``: it never sees the password) is not
involved at all. That is precisely what keeps the vault operator-opaque at rest.

**The account fragment.** A credential dashboard: the public key (for the
out-of-band ``user-authorize`` step), **write-only** secret upload/replace/delete into
the vault-encrypted ``~/.euler/env`` (values are never rendered back), and the gh /
Claude Code sign-in state (the actual logins run in the web shell).

**Reset.** ``POST /internal/vault-reset`` — socket-peer only, pushed by the auth
service when a password *reset* completes — destroys the vault: an SRP reset shares
nothing with the vault, so the old ``VK`` is unrecoverable *by design* and leaving the
blobs around would only misrepresent the state. A password *change* instead rides
``POST /vault/rewrap`` and the vault survives.
"""
from __future__ import annotations

__all__ = ['add_vault_routes', 'reset_vault_and_lock']

import asyncio
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from aiohttp import web
from cryptography.exceptions import InvalidTag

from solver.crypto import vault
from solver.crypto.ciphers import load_private_key, public_key_hex, read_master_key
from solver.crypto.config import config as crypto_config
from solver.web.site.app import requires
from solver.web.site.render import render

#: The account floor: every rung may read (and here, act on) its *own* account.
_VAULT_REQUIRES: str = 'reader'

#: Env entry names: dotenv-style upper-snake identifiers.
_NAME_RE = re.compile(r'^[A-Z][A-Z0-9_]{0,63}$')
_VALUE_MAX: int = 4096

_PK_LEN: int = 32   # PBKDF2-derived password key
_SALT_LEN: int = 16  # the SRP salt width


# ==================================================================================================================== #
#                                               small helpers
# ==================================================================================================================== #
def _hex_bytes(value: Any, length: int) -> bytes | None:
    """Decode *value* as exactly *length* bytes of hex, else None."""
    if not isinstance(value, str):
        return None
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        return None
    return raw if len(raw) == length else None


def _drop_key_caches() -> None:
    """Clear the cached private key / master key so the next read sees the new vault state."""
    load_private_key.cache_clear()
    read_master_key.cache_clear()


def _unlocked() -> bool:
    return vault.session_vault_key() is not None


def _public_key_state() -> tuple[str, str]:
    """The account page's pubkey line: a ``(state, value)`` pair.

    States: ``key`` (value = the hex to hand to the admin), ``locked`` (encrypted id,
    no session VK), ``none`` (no keypair yet — run ``user`` in the shell).
    """
    if not crypto_config['private_key_file'].exists():
        return 'none', ''
    load_private_key.cache_clear()      # the shell may have regenerated the key since our last look
    try:
        return 'key', public_key_hex(load_private_key().public_key())
    except ValueError:
        return 'locked', ''


def _env_lines(vault_key: bytes) -> list[str]:
    """The decrypted lines of ``~/.euler/env`` (empty when the file is absent)."""
    env_file: Path = crypto_config['env_file']
    if not env_file.exists():
        return []
    text = vault.decrypt_secret(vault_key, env_file.read_bytes()).decode('utf-8')
    return text.splitlines()


def _write_env_lines(vault_key: bytes, lines: list[str]) -> None:
    """Encrypt the env lines under ``VK`` and write them back (0600)."""
    env_file: Path = crypto_config['env_file']
    body = ('\n'.join(lines) + '\n') if lines else ''
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_bytes(vault.encrypt_secret(vault_key, body.encode('utf-8')))
    env_file.chmod(0o600)


def _secret_names(vault_key: bytes) -> list[str]:
    """The NAMES stored in the env file — never the values (write-only surface)."""
    names = [line.split('=', 1)[0].strip() for line in _env_lines(vault_key)
             if '=' in line and not line.lstrip().startswith('#')]
    return sorted(set(filter(None, names)))


def _tool_status(binary: str, args: list[str], timeout: float = 8.0) -> str:
    """``signed in`` / ``not signed in`` / ``not installed`` for a CLI credential check."""
    path = shutil.which(binary)
    if path is None:
        return 'not installed'
    try:
        proc = subprocess.run([path, *args], capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return 'not signed in'
    return 'signed in' if proc.returncode == 0 else 'not signed in'


def _claude_status() -> str:
    """Claude Code sign-in state: the CLI plus its stored credentials (the login runs in the shell)."""
    if shutil.which('claude') is None:
        return 'not installed'
    creds = Path(os.environ.get('HOME', str(Path.home()))) / '.claude' / '.credentials.json'
    return 'signed in' if creds.exists() else 'not signed in'


def reset_vault_and_lock() -> list[str]:
    """Destroy the vault + its secrets and drop every in-process key cache."""
    removed = vault.reset_vault()
    _drop_key_caches()
    return removed


# ==================================================================================================================== #
#                                               routes
# ==================================================================================================================== #
def add_vault_routes(app: web.Application) -> None:
    """Register the vault + account routes on the per-user app."""

    @requires(_VAULT_REQUIRES)
    async def vault_status(_request: web.Request) -> web.Response:
        """``GET /vault/status`` — existence, lock state, and the KDF parameters.

        The salt + iterations are not secret (they are useless without the password) and
        let the browser derive the *old* ``PK`` for the stale-vault recovery path.
        """
        data = vault.read_vault()
        body: dict[str, Any] = {'vault': data is not None, 'unlocked': _unlocked()}
        if data is not None:
            body['salt'] = data['salt']
            body['iterations'] = data['iterations']
        return web.json_response(body)

    @requires(_VAULT_REQUIRES)
    async def vault_unlock(request: web.Request) -> web.Response:
        """``POST /vault/unlock`` ``{pk, salt}`` — unlock, or initialise on first login.

        No vault yet → mint one wrapped under this ``PK`` (recording the SRP ``salt`` so
        every future session derives the same key) and encrypt any plaintext secrets.
        A ``PK`` that does not match → 409 ``stale`` (a password reset orphaned the
        vault, or an old tab holds a dead key) — never destructive.
        """
        try:
            body: Any = await request.json()
        except ValueError:
            return web.json_response({'error': 'bad request'}, status=400)
        pk = _hex_bytes(body.get('pk'), _PK_LEN) if isinstance(body, dict) else None
        if pk is None:
            return web.json_response({'error': 'pk required'}, status=400)
        if not vault.vault_exists():
            salt = _hex_bytes(body.get('salt'), _SALT_LEN)
            if salt is None:
                return web.json_response({'error': 'salt required to initialise'}, status=400)
            vault_key = vault.init_vault_from_pk(pk, salt)
            vault.write_session_key(vault_key)
            _drop_key_caches()
            return web.json_response({'unlocked': True, 'initialized': True})
        if _unlocked():
            return web.json_response({'unlocked': True, 'initialized': False})
        try:
            vault_key = vault.unlock_vault_with_pk(pk)
        except InvalidTag:
            return web.json_response({'unlocked': False, 'stale': True}, status=409)
        vault.write_session_key(vault_key)
        _drop_key_caches()
        return web.json_response({'unlocked': True, 'initialized': False})

    @requires(_VAULT_REQUIRES)
    async def vault_rewrap(request: web.Request) -> web.Response:
        """``POST /vault/rewrap`` ``{old_pk, new_pk, new_salt}`` — the vault survives a password change.

        Re-wraps only the small ``VK`` blob under the new ``PK``; the secrets are never
        re-encrypted. Also serves the stale-vault recovery: the browser derives the old
        ``PK`` from the *previous* password and the vault's stored salt (`/vault/status`).
        """
        try:
            body = await request.json()
        except ValueError:
            return web.json_response({'error': 'bad request'}, status=400)
        if not isinstance(body, dict):
            return web.json_response({'error': 'bad request'}, status=400)
        old_pk = _hex_bytes(body.get('old_pk'), _PK_LEN)
        new_pk = _hex_bytes(body.get('new_pk'), _PK_LEN)
        new_salt = _hex_bytes(body.get('new_salt'), _SALT_LEN)
        if old_pk is None or new_pk is None or new_salt is None:
            return web.json_response({'error': 'old_pk, new_pk, new_salt required'}, status=400)
        if not vault.vault_exists():
            return web.json_response({'error': 'no vault'}, status=404)
        try:
            vault.rewrap_vault_with_pk(old_pk, new_pk, new_salt)
        except InvalidTag:
            return web.json_response({'rewrapped': False, 'stale': True}, status=409)
        vault_key = vault.unlock_vault_with_pk(new_pk)
        vault.write_session_key(vault_key)          # the rewrapping session is unlocked too
        _drop_key_caches()
        return web.json_response({'rewrapped': True})

    async def _account_fragment(request: web.Request, status: int = 200) -> web.Response:
        """Render the vault panel (htmx fragment) reflecting the current vault state."""
        unlocked = _unlocked()
        pubkey_state, pubkey = _public_key_state()
        loop = asyncio.get_running_loop()
        gh = await loop.run_in_executor(None, _tool_status, 'gh', ['auth', 'status'])
        claude = await loop.run_in_executor(None, _claude_status)
        vault_key = vault.session_vault_key()
        return render(request, 'account_vault.html', {
            'vault_exists': vault.vault_exists(),
            'unlocked': unlocked,
            'pubkey_state': pubkey_state,
            'pubkey': pubkey,
            'secret_names': _secret_names(vault_key) if vault_key is not None else [],
            'gh_status': gh,
            'claude_status': claude,
        }, status=status)

    @requires(_VAULT_REQUIRES)
    async def account_vault(request: web.Request) -> web.Response:
        """``GET /account/vault`` — the account page's credential panel."""
        return await _account_fragment(request)

    @requires(_VAULT_REQUIRES)
    async def secret_upsert(request: web.Request) -> web.Response:
        """``POST /account/secret`` — add/replace one env entry, write-only."""
        form = await request.post()
        name = str(form.get('name', '')).strip().upper()
        value = str(form.get('value', '')).strip()
        vault_key = vault.session_vault_key()
        if vault_key is None:
            return await _account_fragment(request, status=409)
        if not _NAME_RE.match(name) or not value or len(value) > _VALUE_MAX or any(
                c in value for c in '\r\n\x00'):
            return await _account_fragment(request, status=400)
        lines = [line for line in _env_lines(vault_key)
                 if line.split('=', 1)[0].strip() != name]
        lines.append(f'{name}={value}')
        _write_env_lines(vault_key, lines)
        return await _account_fragment(request)

    @requires(_VAULT_REQUIRES)
    async def secret_delete(request: web.Request) -> web.Response:
        """``POST /account/secret/delete`` — drop one env entry by name."""
        form = await request.post()
        name = str(form.get('name', '')).strip()
        vault_key = vault.session_vault_key()
        if vault_key is None:
            return await _account_fragment(request, status=409)
        lines = _env_lines(vault_key)
        kept = [line for line in lines if line.split('=', 1)[0].strip() != name]
        if len(kept) != len(lines):
            _write_env_lines(vault_key, kept)
        return await _account_fragment(request)

    async def internal_vault_reset(request: web.Request) -> web.Response:
        """``POST /internal/vault-reset`` — the auth service's reset push.

        Socket-peer only (Caddy never routes ``/internal/*``): a completed password
        *reset* means the old ``VK`` is unrecoverable by design, so remove the vault and
        its ciphertext rather than leave a stale blob under the dead ``PK``. The next
        login initialises a fresh vault and the user re-provisions (``user --regen`` +
        re-upload).
        """
        removed = reset_vault_and_lock()
        return web.json_response({'reset': True, 'removed': removed})

    app.add_routes([
        web.get('/vault/status', vault_status),
        web.post('/vault/unlock', vault_unlock),
        web.post('/vault/rewrap', vault_rewrap),
        web.get('/account/vault', account_vault),
        web.post('/account/secret', secret_upsert),
        web.post('/account/secret/delete', secret_delete),
        web.post('/internal/vault-reset', internal_vault_reset),
    ])
