#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Cipher key management: create, persist, rotate and share the crypto key material.

This is the **interactive** half of `solver.crypto` -- all user interaction (password prompts, share
entry, confirmations) lives here, and nowhere else. It owns the lifecycle of two keys:

- The **asymmetric** identity: an X25519 key pair. The private key is generated here and written
  **plain** (unencrypted PKCS8 PEM) to `~/.euler/id` -- a machine-local `0600` file outside the
  repo, whose file permissions are its protection -- so the non-interactive load path
  (`solver.crypto.ciphers.load_private_key`) needs no password.
- The **symmetric** master key: a single 32-byte AES key, wrapped to each authorised user's public
  key in `keys/enc-key.json` -- a `{<public-key-hex>: <locked-master-key-hex>}` map plus the
  reserved `verify` ciphertext and `owners` attribution map. Authority is
  **proof-of-possession**: anyone who can unwrap and verify the current master key may rotate it,
  authorise another public key, or split it into shares. `owners` records *whose* key each entry
  is, written only by `user-authorize`, read only by `users purge` -- it is bookkeeping and grants
  nothing.

The non-interactive primitives (load, lock/unlock, encrypt/decrypt) come from `solver.crypto.ciphers`
and the configuration from `solver.crypto.config`; this module never re-implements them. The git
filter (`solver.crypto.gitfilter`) does not import this module.

Shell commands registered here: `user`, `rekey`, `authorize`, `key-split`, `key-reconstruct`.
"""
from __future__ import annotations

__all__ = ['key_reconstruct', 'key_rekey', 'key_split', 'revoke_keys', 'unlock_session', 'user',
           'user_authorize', 'vault']

import atexit
import os
import re
from datetime import datetime, timezone
from json import dumps
from pathlib import Path
from secrets import randbelow, token_bytes
from subprocess import run
from typing import Any, Iterable, Literal

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.auth.identity import system_slug
from solver.config import config as app_config
from solver.core import osc
from solver.crypto import vault as vault_mod
from solver.crypto.ciphers import (authorised_keys, encrypt_blob, key_owners, load_private_key, lock,
                                   public_key_hex, read_enc_key_file, read_master_key, verify_master_key)
from solver.crypto.config import config
from solver.shell import console, register
from solver.utils.shell_utils import confirm

#: The subject `_request_authorization` files a key request under, and the marker
#: `user-authorize <msg-id>` requires before it will read a key out of a message body —
#: so an arbitrary `msg send` is never mined for hex.
_KEY_REQUEST_SUBJECT: str = 'Key authorization request from '

#: A public key on the wire and in enc-key.json: 32 bytes of lowercase hex.
_PUBLIC_KEY_RE = re.compile(r'\b[0-9a-f]{64}\b')

#: A spool thread id (`secrets.token_hex(8)`) — half a public key's length, which is what
#: lets `user-authorize` take either without a flag to say which it was given.
_THREAD_ID_RE = re.compile(r'[0-9a-f]{16}')


def _now_stamp() -> str:
    """UTC now in ISO-8601 — the `since` field of an ownership record."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


# ==================================================================================================================== #
#                                       asymmetric key: create + persist
# ==================================================================================================================== #
def _rotate_backups(key_file: Path) -> None:
    """Rotate up to `private_key_backups` rolling backups of key_file (.1 newest ... .N oldest)."""
    if not key_file.exists():
        return
    keep: int = config['private_key_backups']
    oldest: Path = key_file.with_suffix(f'.{keep}')
    if oldest.exists():
        oldest.unlink()
    for i in range(keep - 1, 0, -1):
        backup: Path = key_file.with_suffix(f'.{i}')
        if backup.exists():
            backup.rename(key_file.with_suffix(f'.{i + 1}'))
    key_file.rename(key_file.with_suffix('.1'))


def _persist_private_key(private_key: X25519PrivateKey) -> None:
    """Write the private key to disk `0600` (rotating backups) -- vault-encrypted when one is unlocked.

    With a vault present and this session holding its ``VK``, the PEM is encrypted at rest like every
    vault secret -- so `user --regen` never downgrades an encrypted `id` back to plaintext. With
    no vault (the pre-vault operator setup) the key is written plain, protected by the `0600` secrets
    dir as before.
    """
    key_file: Path = config['private_key_file']
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.parent.chmod(0o700)
    data: bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    at_rest: str = 'plain, machine-local `0600`'
    # Every refusal must happen BEFORE the backup rotation: a refused persist that has
    # already rotated leaves no id file at all — worse than either state it refused.
    if vault_mod.vault_exists():
        vault_key: bytes | None = vault_mod.session_vault_key()
        if vault_key is None:
            console.print('[error]error:[/error] a vault exists but this session cannot unlock it; '
                          'refusing to write the private key in plaintext beside it.')
            raise PermissionError('vault locked')
        data = vault_mod.encrypt_secret(vault_key, data)
        at_rest = 'vault-encrypted'
    _rotate_backups(key_file)
    key_file.write_bytes(data)
    key_file.chmod(0o600)
    load_private_key.cache_clear()
    read_master_key.cache_clear()
    console.print(f'[success]Private key written to [accent]{key_file}[/accent] ({at_rest})[/success]')


def _create_user_key() -> X25519PrivateKey:
    """Generate a fresh X25519 key pair, persist it plain (`0600`), and return the private key."""
    private_key: X25519PrivateKey = x25519.X25519PrivateKey.generate()
    _persist_private_key(private_key)
    return private_key


# ==================================================================================================================== #
#                                       master (symmetrical) key: persist + rotate
# ==================================================================================================================== #
def _write_enc_key_file(data: dict[str, Any]) -> None:
    """Serialise keys/enc-key.json and clear the cached master key so the next read picks it up."""
    enc_file: Path = config['enc_key_file']
    enc_file.parent.mkdir(parents=True, exist_ok=True)
    enc_file.write_text(dumps(data, indent=2))
    read_master_key.cache_clear()
    pubkeys: int = len(authorised_keys(data))
    console.print(f'[success]Wrote [accent]{enc_file}[/accent] ({pubkeys} authorised public key(s))[/success]')


def _wrapped_for_all(master_key: bytes, public_keys: list[str],
                     owners: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Build the enc-key.json body: master_key wrapped to each public key, plus the reserved entries.

    *owners* is carried through **pruned to the keys being wrapped** — a rotation that drops a
    key must drop its attribution with it, or the file would keep naming the owner of an entry
    that no longer exists and `users purge` would count a ghost.
    """
    data: dict[str, Any] = {pub: lock(X25519PublicKey.from_public_bytes(bytes.fromhex(pub)), master_key)
                            for pub in public_keys}
    data[config['enc_key_verify']] = encrypt_blob(config['verify_text'], master_key).hex()
    kept = {pub: record for pub, record in (owners or {}).items() if pub in data}
    if kept:
        data[config['enc_key_owners']] = kept
    return data


def revoke_keys(public_keys: Iterable[str]) -> int:
    """Drop *public_keys* and their ownership records from enc-key.json; return how many went.

    The removal half of :func:`user_authorize`, and the mutation behind ``users purge`` —
    which owns *deciding* what is stale (it needs the account roster, which is the auth
    service's to know) while every write to this file stays here, in the one module that
    persists key material.

    **This is not revocation.** A holder who has already unwrapped the master key still has
    it, and every committed blob stays decryptable with it forever; dropping an entry only
    stops that key unwrapping *future* copies of the file. Revoking access means purging and
    then :func:`key_rekey`, which re-wraps a *new* master key to the survivors and
    re-encrypts the tree. Callers must say so rather than let a purge read as a lock-out.

    Refuses to empty the file: a keys/enc-key.json with no public keys in it is one nobody
    can decrypt and nobody can rekey — an unrecoverable state, reached by a typo.
    """
    data: dict[str, Any] = read_enc_key_file()
    drop = {key.strip().lower() for key in public_keys}
    keep = [key for key in authorised_keys(data) if key not in drop]
    if not keep:
        console.print('[error]error:[/error] refusing to remove every authorised key — '
                      'the file would be unreadable and unrecoverable')
        return 0
    removed = [key for key in authorised_keys(data) if key in drop]
    if not removed:
        return 0
    owners = {pub: record for pub, record in key_owners(data).items() if pub not in drop}
    for key in removed:
        del data[key]
    if owners:
        data[config['enc_key_owners']] = owners
    else:
        data.pop(config['enc_key_owners'], None)
    _write_enc_key_file(data)
    return len(removed)


@register(requires='admin', help_text='Rotate the enc key and re-wrap to users.', aliases=('rekey',))
def key_rekey() -> int:
    """Rotate to a new master key (proof-of-possession), re-wrap to all users, and renormalise blobs.

    Because the git filter is deterministic, every committed blob depends on the master key, so a
    rotation re-encrypts the tracked private files via `git add --renormalize`.
    """
    try:
        read_master_key()  # proof of authority: must currently hold and verify the master key
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] refusing to rekey -- current key check failed ({exc})')
        return 1
    if not confirm('Rotate the master key and re-encrypt all private files?'):
        console.print('[muted]Rekey cancelled.[/muted]')
        return 1
    data: dict[str, Any] = read_enc_key_file()
    new_master: bytes = token_bytes(32)
    _write_enc_key_file(_wrapped_for_all(new_master, authorised_keys(data), key_owners(data)))
    console.print('[muted]Re-encrypting tracked private files...[/muted]')
    run(['git', 'add', '--renormalize', '--', 'solutions/private'], cwd=config['root_dir'], check=False)
    console.print('[success]Master key rotated; review `git status` and commit the re-encrypted blobs.[/success]')
    return 0


def _resolve_key_request(thread_id: str) -> tuple[str, str] | None:
    """Read a key-authorization thread and return ``(public_key, identity)``, or None.

    The identity comes from the thread's **author**, not from its text: the spool resolved
    that box from ``SO_PEERCRED`` when the request was filed, so it is the one field in a
    message a sender cannot dress up as somebody else. Only the key itself is read out of
    the body, under rules that refuse rather than guess:

    - the subject must be the one ``_request_authorization`` files under, so an arbitrary
      ``msg send`` is never mined for hex;
    - the body must contain **exactly one** 64-hex token. Zero or several means the message
      is not the request we know how to work, and the operator is told to pass the key
      itself. A grant is not a thing to infer from ambiguous text.
    """
    from solver.web.msg.notify import read_thread
    thread: dict[str, Any] | None = read_thread(thread_id)
    if thread is None:
        console.print(f'[error]error:[/error] cannot read message [accent]{thread_id}[/accent] '
                      '(no such thread, not yours to read, or the spool is unreachable)')
        return None
    if not str(thread.get('subject', '')).startswith(_KEY_REQUEST_SUBJECT):
        console.print(f'[error]error:[/error] message [accent]{thread_id}[/accent] is not a key '
                      'authorization request — authorise the public key directly instead')
        return None
    found = _PUBLIC_KEY_RE.findall(str(thread.get('body', '')))
    if len(found) != 1:
        console.print(f'[error]error:[/error] found [accent]{len(found)}[/accent] public keys in '
                      f'message {thread_id}; expected exactly one — pass the key itself')
        return None
    identity = str(thread.get('author_name') or thread.get('author') or '')
    return found[0], identity


@register(requires='maintainer', aliases=('authorize',),
          help_text='Authorise a public key (hex), or work a key request by message id.')
def user_authorize(target: str, identity: str = '') -> int:
    """Wrap the current master key to a public key and record whose key it is.

    *target* is either form of the same act, told apart by shape:

    - a **64-hex public key** — the direct grant, as before. *identity* is optional and,
      when given, is what the entry is attributed to.
    - a **16-hex message id** — the key-authorization request the collaborator's `user`
      command filed (`msg queue` lists them). The key and the requester are read from the
      thread, the grant is confirmed interactively, and the thread is replied to and marked
      read, so the person waiting learns it happened without anyone composing a message.

    Attribution is written to the ``owners`` entry of enc-key.json and is **bookkeeping,
    not authority**: it grants nothing on its own, and a key with no owner still decrypts.
    It exists so `users purge` can tell whose entry is whose. Only this command writes it —
    `user --regen`'s local re-wrap is a stopgap until the authorized file arrives by
    `git-sync`, so recording ownership there would attribute a file about to be replaced.

    Args:
        target:   a 64-hex public key, or the 16-hex id of a key-authorization message.
        identity: the email or os-login the key belongs to (public-key form only; the
                  message form takes it from the thread's author). Omitted, the entry is
                  authorised but left unattributed — and says so.

    Aliased as `authorize`.
    """
    from solver.web.msg.notify import answer_thread
    token = target.strip().lower()
    thread_id = ''
    if _THREAD_ID_RE.fullmatch(token):
        resolved = _resolve_key_request(token)
        if resolved is None:
            return 1
        thread_id, public_key, identity = token, resolved[0], resolved[1]
    elif _PUBLIC_KEY_RE.fullmatch(token):
        public_key = token
    else:
        console.print('[error]error:[/error] expected a 64-character public key or a '
                      '16-character message id')
        return 1

    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    try:
        pub: X25519PublicKey = X25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
    except ValueError:
        console.print('[error]error:[/error] public_key must be 32 bytes of hex')
        return 1

    # The message form asks before granting: its key came out of free text a collaborator
    # can write, so the operator sees who and what before it lands. The direct form does
    # not — it is the scriptable one, and the operator typed the key themselves.
    if thread_id:
        console.print(f'[primary]request from:[/primary] {identity or "unknown"}\n'
                      f'[primary]public key:[/primary]   {public_key}')
        if not confirm('Authorise this key for master-key access?'):
            console.print('[muted]Not authorised.[/muted]')
            return 1

    data: dict[str, Any] = read_enc_key_file()
    data[public_key_hex(pub)] = lock(pub, master_key)
    if identity:
        owners: dict[str, dict[str, str]] = key_owners(data)
        owners[public_key_hex(pub)] = {'slug': system_slug(identity), 'since': _now_stamp(),
                                       'by': system_slug(app_config['subject'].user)}
        data[config['enc_key_owners']] = owners
    _write_enc_key_file(data)
    console.print(f'[success]Public key [accent]{public_key}[/accent] authorised'
                  f'{f" for [accent]{identity}[/accent]" if identity else ""}.[/success]')
    if not identity:
        # Unattributed by choice, and said out loud: `users purge` will not offer this entry
        # as stale (it cannot know whose it is), so the operator should know they have opted
        # into keeping it forever unless they purge it by key.
        console.print('[muted]No identity recorded — this entry stays unattributed and '
                      '`users purge` will never offer it.[/muted]')
    console.print('[muted]Commit and push keys/enc-key.json (`git-publish keys`) — the grant '
                  'reaches the collaborator when they `git-sync`.[/muted]')
    if thread_id:
        if answer_thread(thread_id, f'Your public key {public_key} is authorised for the private '
                                    f'solutions.\n\nIt reaches your clone once the updated '
                                    f'keys/enc-key.json is pushed — run `git-sync` then, and the '
                                    f'private solutions decrypt in place.'):
            console.print(f'[muted]Replied on message [accent]{thread_id}[/accent] and marked it '
                          'read (dismiss it with `msg dismiss` when you are done with it).[/muted]')
        else:
            console.print(f'[warning]note:[/warning] could not reply on message {thread_id} — '
                          'the authorization stands; tell them yourself.')
    return 0


# ==================================================================================================================== #
#                                               user identity
# ==================================================================================================================== #
@register(requires='reader', help_text="Show euler user, public key & enc-key access; --regen for new key-pair.")
def user(regen: bool = False) -> int:
    """Show the solver user, the current identity and whether it can decrypt; create a key pair on first run or --regen.

    A key pair is created only when the identity file is **truly absent** (first run) or on
    an explicitly confirmed ``--regen``. An id file that *exists but cannot be read* — the
    vault is locked, the session key is stale, the vault file was lost — is a **vault
    failure to fix, never a reason to mint a new identity**: replacing the key would
    silently orphan the real one (and with it any enc-key authorization it carries).
    """
    app_user = app_config['subject']
    console.print(f'[primary]solver user:[/primary] {app_user.user} [muted]({app_user.profile})[/muted]')
    id_file: Path = config['private_key_file']
    private_key: X25519PrivateKey | None = None
    minted: bool = False        # a key was created here — the only path that files a request
    if id_file.exists():
        try:
            private_key = load_private_key()
        except ValueError as exc:
            console.print(f'[error]error:[/error] your identity file exists but cannot be read: {exc}')
            if not regen:
                console.print('[muted]NOT creating a new key over it. Unlock the vault first '
                              '(web: sign out and back in; terminal: check [accent]vault status[/accent] '
                              'and ~/.euler/vault). To deliberately REPLACE the unreadable identity, '
                              'run [accent]user --regen[/accent].[/muted]')
                return 1
            if not confirm('REPLACE the unreadable identity with a fresh key pair? '
                           '(the old file is kept as a rotated backup; any enc-key access it had is lost)'):
                console.print('[muted]Keeping the existing (unreadable) identity file.[/muted]')
                return 1
    if regen and private_key is not None and not confirm('Replace the existing private key with a new one?'):
        console.print('[muted]Keeping the existing private key.[/muted]')
        regen = False
    if regen or private_key is None:
        # Carry master-key access across the rotation: capture it with the outgoing key *before*
        # replacing it, then re-wrap it to the new key (and revoke the old entry) afterwards.
        carry: tuple[str, bytes] | None = None
        if private_key is not None:
            try:
                carry = (public_key_hex(private_key.public_key()), read_master_key())
            except (FileNotFoundError, KeyError, ValueError):
                carry = None
        try:
            private_key = _create_user_key()
        except PermissionError:
            return 1                     # vault present but locked — persist refused (message printed)
        if carry is not None:
            old_pub, master_key = carry
            data: dict[str, str] = read_enc_key_file()
            data.pop(old_pub, None)  # revoke the replaced key's access
            data[public_key_hex(private_key.public_key())] = lock(private_key.public_key(), master_key)
            _write_enc_key_file(data)
        # A new identity is exactly what the account page's public-key panel shows —
        # nudge it to re-read (a no-op unless it is the visible pane). Only when a key
        # was actually minted: a bare `user` status view changed nothing.
        osc.account_changed()
        minted = True
    pub: str = public_key_hex(private_key.public_key())
    try:
        read_master_key()
        console.print(f'[primary]public key:[/primary] {pub}\n[success]✓ can encrypt/decrypt[/success]')
    except (FileNotFoundError, KeyError, ValueError):
        console.print(f'[primary]public key:[/primary] {pub}\n[error]✗ cannot encrypt/decrypt[/error]')
        console.print('[muted]Have an existing user `authorize` this public key, or `key-reconstruct` '
                      'from shares.[/muted]')
        if minted:
            _request_authorization(app_user.user, pub)
    return 0


def _request_authorization(identity: str, public_key: str) -> None:
    """File a key-authorization request with staff for a freshly minted key.

    Only on the path that needs it: a key was **just minted** *and* it cannot decrypt,
    so somebody with the master key has to run ``user-authorize`` on it. A key that
    already decrypts needs nothing, and a bare ``user`` status view is not a request.

    This is why the message layer exists (:mod:`solver.web.msg.notify`) — before it, the
    account page told the collaborator to "copy your public key to the admin and wait",
    with no mechanism behind the waiting. Best-effort: the key is minted either way, so a
    spool that is down or absent costs a nudge and nothing else, and the one line printed
    here reflects which of the two happened rather than claiming a delivery that failed.
    """
    from solver.web.msg.notify import notify_staff
    # The subject is the constant `user-authorize <msg-id>` matches on, and the body carries
    # exactly one public key — the two rules that make this thread machine-workable. Keep both
    # true when editing this text: a reworded subject silently turns every future request back
    # into copy-and-paste, and a second hex token in the body makes it refuse.
    sent = notify_staff(
        f'{_KEY_REQUEST_SUBJECT}{identity}',
        f'{identity} minted a new key pair and cannot decrypt the private solutions yet.\n\n'
        f'public key: {public_key}\n\n'
        f'To grant access, run:\n'
        f'    user-authorize <the id of this message>\n')
    if sent:
        console.print('[muted]A key-authorization request has been sent to the maintainers.[/muted]')


# ==================================================================================================================== #
#                                       per-user vault (envelope encryption of id + env)
# ==================================================================================================================== #
def _own_key_file(path: Path) -> None:
    """Take ownership of a session key file WE created: remove it when this process ends.

    Only ever called for a file this process wrote. A key file we **inherited** must never be
    removed: on the web path the per-user service writes it and shares it across every shell
    that user has open, so cleaning it up on one shell's exit would lock the others (and the
    service's own session) out mid-flow. Ownership is the whole distinction, and it is why
    this cannot live in :func:`~solver.crypto.vault.write_session_key`, which cannot know who
    is calling it.

    Best-effort: a SIGKILL runs no handler, so a crashed shell still leaves its file behind
    until logout clears the tmpfs. This bounds the pile to live shells rather than to every
    shell that ever ran.
    """
    atexit.register(lambda: path.unlink(missing_ok=True))


def unlock_session(interactive: bool = True) -> bytes | None:
    """Establish this process tree's vault key, asking the operator only if nothing else can.

    The terminal's whole unlock path, and the one place a password is ever *prompted for*. The
    order is: an existing session key file, then ``$EULER_VAULT_PASSWORD`` (both handled by
    :func:`~solver.crypto.vault.ensure_session_key`, non-interactively), and only then the
    operator. A shell calls this once at startup; children -- notably the git filter, which has
    no terminal and cannot be asked anything -- inherit the key file it materialises.

    Any key file this call *creates* is removed at process exit (:func:`_own_key_file`); one it
    merely found is left alone, because it belongs to whoever wrote it.

    Returns the ``VK``, or None when there is no vault, when the vault stays locked, or when
    *interactive* is False and no env password answered. A locked session is not an error: it
    means the private solutions and `claude-api` are unavailable, and everything else works.
    """
    if not vault_mod.vault_exists():
        return None
    # ensure_session_key() writes a key file itself when the env password answers, so compare
    # the exported path across the call: a change means the file is new, and ours.
    before: str = os.environ.get(config['vault_key_env'], '')
    if (vault_key := vault_mod.ensure_session_key()) is not None:
        after: str = os.environ.get(config['vault_key_env'], '')
        if after and after != before:
            _own_key_file(Path(after))
        return vault_key
    if not (interactive and console.is_interactive):
        return None
    password: str = console.input('[accent]Vault password:[/accent] ', password=True)
    if not password:
        return None
    try:
        vault_key = vault_mod.unlock_vault(password)
    except InvalidTag:
        console.print('[error]error:[/error] wrong password — the vault stays locked '
                      '(private solutions and `claude-api` are unavailable this session).')
        return None
    _own_key_file(vault_mod.write_session_key(vault_key))
    load_private_key.cache_clear()
    read_master_key.cache_clear()
    return vault_key


def _prompt_new_password(prompt: str) -> str | None:
    """Prompt for a password twice (hidden); return it, or None on mismatch / empty input."""
    first: str = console.input(f'[accent]{prompt}:[/accent] ', password=True)
    if not first:
        console.print('[error]error:[/error] password must not be empty')
        return None
    if console.input('[accent]Confirm password:[/accent] ', password=True) != first:
        console.print('[error]error:[/error] passwords do not match')
        return None
    return first


def _orphaned_vault_files() -> list[str]:
    """Vault-encrypted secret files with NO vault file to unwrap their key — a broken state.

    Their ``VK`` is unrecoverable without ``~/.euler/vault``, so they are unreadable by
    anyone; every caller must surface this loudly rather than treat it as "no vault yet".
    """
    if vault_mod.vault_exists():
        return []
    return [p.name for p in (config['private_key_file'], config['env_file'])
            if p.exists() and vault_mod.is_vault_encrypted(p.read_bytes())]


def _vault_status() -> int:
    """Report whether the vault exists, the state of each secret file, and whether this
    session's key actually decrypts them (a stale/foreign key is flagged, not hidden)."""
    id_file: Path = config['private_key_file']
    env_file: Path = app_config.env_file
    vault_key: bytes | None = vault_mod.session_vault_key() if vault_mod.vault_exists() else None

    def _state(path: Path) -> str:
        if not path.exists():
            return '[muted]absent[/muted]'
        raw = path.read_bytes()
        if not vault_mod.is_vault_encrypted(raw):
            return '[warning]plaintext[/warning]'
        if not vault_mod.vault_exists():
            return '[error]encrypted — but the vault file is MISSING (key unrecoverable)[/error]'
        if vault_key is None:
            return '[success]encrypted[/success] [muted](locked — cannot verify)[/muted]'
        try:
            vault_mod.decrypt_secret(vault_key, raw)
            return '[success]encrypted[/success] [muted](decrypts)[/muted]'
        except InvalidTag:
            return '[error]encrypted — the session key does NOT decrypt it (foreign vault?)[/error]'

    if orphans := _orphaned_vault_files():
        console.print(f'[error]BROKEN:[/error] {", ".join(orphans)} are vault-encrypted but '
                      '~/.euler/vault is missing — restore it from backup, or recover deliberately '
                      '([accent]user --regen[/accent] for the id; re-create env).')
    elif not vault_mod.vault_exists():
        console.print('[warning]No vault.[/warning] `id` and `env` rest in plaintext; run '
                      '[accent]vault init[/accent] to encrypt them.')
    else:
        unlocked: bool = vault_key is not None
        console.print(f'[primary]vault:[/primary] present · '
                      f'session {"[success]unlocked[/success]" if unlocked else "[error]locked[/error]"}')
    console.print(f'[primary]id  ({id_file}):[/primary] {_state(id_file)}')
    console.print(f'[primary]env ({env_file}):[/primary] {_state(env_file)}')
    return 0


@register(requires='reader',
          help_text='Manage the per-user secrets vault: status | init | unlock | change-password.')
def vault(action: Literal['status', 'init', 'unlock', 'change-password'] = 'status') -> int:
    """Encrypt this user's `id` + `env` at rest under a password-derived vault key.

    - `status` (default): show whether the vault exists, which secret files are encrypted, and
      whether this session can decrypt them.
    - `init`: create the vault and migrate the existing plaintext `id`/`env` into it in place, then
      unlock the current session. Prompts for a new password.
    - `unlock`: unlock a locked session (the shell asks at startup; this is the retry — after a
      typo, or once you have the password to hand).
    - `change-password`: re-wrap the vault key under a new password (the secrets are not re-encrypted).

    The password is never stored: set `$EULER_VAULT_PASSWORD` for a non-interactive unlock (a script,
    CI), otherwise you are asked once per shell.
    """
    if action == 'status':
        return _vault_status()

    if action == 'unlock':
        if not vault_mod.vault_exists():
            console.print('[warning]No vault.[/warning] Nothing to unlock; run '
                          '[accent]vault init[/accent] to encrypt `id` and `env`.')
            return 1
        if vault_mod.session_vault_key() is not None:
            console.print('[success]Already unlocked.[/success]')
            return 0
        return 0 if unlock_session() is not None else 1

    if action == 'init':
        if vault_mod.vault_exists():
            console.print('[error]error:[/error] a vault already exists; use `vault change-password` '
                          'to change the password.')
            return 1
        if orphans := _orphaned_vault_files():
            # A fresh vault would LOOK healthy while these stay encrypted under the lost
            # key forever — refuse rather than paper over a broken state.
            console.print(f'[error]error:[/error] {", ".join(orphans)} are already vault-encrypted '
                          'but ~/.euler/vault is missing — their key is unrecoverable without it. '
                          'Restore the vault file from backup, or remove/replace the unreadable '
                          'files first ([accent]user --regen[/accent] re-mints the id).')
            return 1
        password: str | None = _prompt_new_password('New vault password')
        if password is None:
            return 1
        vault_key: bytes = vault_mod.init_vault(password)
        # Keeps this shell working (exports EULER_VAULT_KEY_FILE); ours, so it goes at exit.
        _own_key_file(vault_mod.write_session_key(vault_key))
        encrypted: list[str] = vault_mod.encrypt_secret_files(vault_key)
        load_private_key.cache_clear()
        read_master_key.cache_clear()
        console.print(f'[success]Vault initialised.[/success] Encrypted: '
                      f'[accent]{", ".join(encrypted) or "nothing (no plaintext secrets found)"}[/accent].')
        return 0

    # change-password
    if not vault_mod.vault_exists():
        console.print('[error]error:[/error] no vault to change; run `vault init` first.')
        return 1
    current: str = console.input('[accent]Current vault password:[/accent] ', password=True)
    try:
        vault_mod.unlock_vault(current)
    except InvalidTag:
        console.print('[error]error:[/error] wrong password.')
        return 1
    new_password: str | None = _prompt_new_password('New vault password')
    if new_password is None:
        return 1
    vault_mod.rewrap_vault(current, new_password)
    console.print('[success]Vault password changed.[/success]')
    if os.environ.get(config['vault_password_env']):
        console.print('[warning]note:[/warning] [accent]$'
                      f'{config["vault_password_env"]}[/accent] still holds the OLD password — '
                      'update it wherever it is set, or the next non-interactive unlock fails.')
    return 0


# ==================================================================================================================== #
#                                       n of m secret sharing (Shamir over GF(2**521-1))
# ==================================================================================================================== #
#: 13th Mersenne prime; comfortably larger than a 256-bit secret.
_PRIME: int = 2 ** 521 - 1
#: Length of the master key in bytes, and the hex width sufficient for any value < _PRIME.
_SECRET_BYTES: int = 32
_HEX_WIDTH: int = 131


def _eval_poly(poly: list[int], x: int) -> int:
    """Evaluate `poly` at `x` (Horner's method) modulo `_PRIME`."""
    result: int = 0
    for coeff in reversed(poly):
        result = (result * x + coeff) % _PRIME
    return result


def _interpolate_at_zero(points: list[tuple[int, int]]) -> int:
    """Lagrange-interpolate the polynomial value at `x = 0` from `points` modulo `_PRIME`."""
    result: int = 0
    for i, (xi, yi) in enumerate(points):
        num: int = 1
        den: int = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            num = (num * -xj) % _PRIME
            den = (den * (xi - xj)) % _PRIME
        result = (result + yi * num * pow(den, -1, _PRIME)) % _PRIME
    return result


def _split_secret(secret: bytes, num_shares: int, threshold: int) -> list[str]:
    """Split a 32-byte key into `num_shares` shares; any `threshold` reconstruct it. Each share is 262 hex chars."""
    if len(secret) != _SECRET_BYTES:
        raise ValueError(f'secret must be exactly {_SECRET_BYTES} bytes, got {len(secret)}')
    if not 1 <= threshold <= num_shares:
        raise ValueError('require 1 <= threshold <= num_shares')
    poly: list[int] = [int.from_bytes(secret, 'big')] + [randbelow(_PRIME) for _ in range(threshold - 1)]
    xs: set[int] = set()
    while len(xs) < num_shares:
        xs.add(randbelow(_PRIME - 1) + 1)
    return [f'{x:0{_HEX_WIDTH}x}{_eval_poly(poly, x):0{_HEX_WIDTH}x}' for x in xs]


def _reconstruct_secret(shares: list[str]) -> bytes:
    """Reconstruct the 32-byte key from `threshold` distinct shares produced by `_split_secret`."""
    if not shares:
        raise ValueError('need at least one share')
    points: list[tuple[int, int]] = []
    seen: set[int] = set()
    for s in shares:
        if len(s) != 2 * _HEX_WIDTH:
            raise ValueError(f'share must be {2 * _HEX_WIDTH} hex chars, got {len(s)}')
        x: int = int(s[:_HEX_WIDTH], 16)
        y: int = int(s[_HEX_WIDTH:], 16)
        if x in seen:
            raise ValueError(f'duplicate share index {x:x}')
        seen.add(x)
        points.append((x, y))
    secret_int: int = _interpolate_at_zero(points)
    if secret_int.bit_length() > _SECRET_BYTES * 8:
        raise ValueError('reconstructed value out of range; wrong threshold or corrupted shares')
    return secret_int.to_bytes(_SECRET_BYTES, 'big')


@register(requires='admin', help_text='Split master key into shares (n-of-m secret sharing).')
def key_split(num_shares: int = 3, threshold: int = 2) -> int:
    """Print `num_shares` Shamir shares of the current master key (threshold needed to reconstruct)."""
    if num_shares < threshold or threshold < 2:
        console.print('[error]error:[/error] threshold must be >= 2 and < num_shares')
        return 1
    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    try:
        shares: list[str] = _split_secret(master_key, num_shares, threshold)
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    for i, share in enumerate(shares, start=1):
        console.print(f'[accent]Master key share {i} of {num_shares}:[/accent]\n[muted]{share}[/muted]\n')
    return 0


@register(requires='reader', help_text='Recover master key from shares.')
def key_reconstruct(threshold: int = 2) -> int:
    """Prompt for `threshold` shares, reconstruct the master key, and store it wrapped to this user."""
    try:
        private_key: X25519PrivateKey = load_private_key()
    except (FileNotFoundError, ValueError) as exc:
        console.print(f'[error]error:[/error] need a private key first ({exc}); run `user`')
        return 1
    shares: list[str] = []
    for i in range(1, threshold + 1):
        shares.append(console.input(f'[accent]Enter master key share {i} of {threshold}:[/accent] ').strip())
    try:
        master_key: bytes = _reconstruct_secret(shares)
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    data: dict[str, Any] = read_enc_key_file() if config['enc_key_file'].exists() else {}
    if config['enc_key_verify'] in data and not verify_master_key(data, master_key):
        console.print('[error]error:[/error] reconstructed key fails verification; wrong shares?')
        return 1
    data[public_key_hex(private_key.public_key())] = lock(private_key.public_key(), master_key)
    data.setdefault(config['enc_key_verify'], encrypt_blob(config['verify_text'], master_key).hex())
    _write_enc_key_file(data)
    console.print(f'[success]Master key reconstructed from {threshold} shares and stored.[/success]')
    return 0
