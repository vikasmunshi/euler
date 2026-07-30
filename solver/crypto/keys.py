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
- The **symmetric** master key: a single 32-byte AES key, held by each user in their own
  `~/.euler/enc-key.json` -- two records, `verify` and the key wrapped to their public key.
  Authority is **proof-of-possession**: anyone who can unwrap and verify it may rotate it, issue
  it to another public key, or split it into shares. Issuing goes through the message spool
  (`user-authorize` sends, `msg act` writes); a rotation of one's own key pair needs nobody.

The non-interactive primitives (load, lock/unlock, encrypt/decrypt) come from `solver.crypto.ciphers`
and the configuration from `solver.crypto.config`; this module never re-implements them. The git
filter (`solver.crypto.gitfilter`) does not import this module.

Shell commands registered here: `user`, `rekey`, `authorize`, `key-split`, `key-reconstruct`.
"""
from __future__ import annotations

__all__ = ['key_reconstruct', 'key_rekey', 'key_split', 'save_issued_key', 'unlock_session',
           'user', 'user_authorize', 'vault', 'write_enc_key_file']

import atexit
import os
import re
from datetime import datetime, timezone
from json import dumps, loads
from pathlib import Path
from secrets import randbelow, token_bytes
from subprocess import run
from typing import Any, Literal

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.config import config as app_config
from solver.core import osc
from solver.crypto import vault as vault_mod
from solver.crypto.ciphers import (enc_key_payload, load_private_key, public_key_hex,
                                   read_enc_key_file, read_master_key, unlock, verify_master_key)
from solver.crypto.config import config
from solver.shell import console, register
from solver.shell import dialogue
from solver.shell.dialogue import Abort, sure, text
from solver.web.auth.commands import registered_public_keys
from solver.web.msg import KEY_ISSUE_SUBJECT, KEY_REQUEST_SUBJECT

#: A public key on the wire and in the enc-key file: 32 bytes of lowercase hex.
_PUBLIC_KEY_RE = re.compile(r'\b[0-9a-f]{64}\b')

#: The JSON object an issue message carries — the payload, wherever it sits in the prose.
_JSON_OBJECT_RE = re.compile(r'\{.*\}', re.DOTALL)

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

    With a vault present and this session holding its `VK`, the PEM is encrypted at rest like every
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
def write_enc_key_file(data: dict[str, str]) -> None:
    """Write this machine's enc-key file (`0600`) and drop the cached master key.

    The file is two records and belongs to this machine alone, so writing it is a local act:
    no commit, no push, nobody else's copy to reconcile with. That is the whole point of
    having moved it out of the checkout.
    """
    enc_file: Path = config['enc_key_file']
    enc_file.parent.mkdir(parents=True, exist_ok=True)
    enc_file.parent.chmod(0o700)
    enc_file.write_text(dumps(data, indent=2))
    enc_file.chmod(0o600)
    read_master_key.cache_clear()


@register(requires='admin', aliases=('rekey',))
def key_rekey() -> int:
    """Rotate the master key and re-issue it to every registered public key.

    **Revocation lives here, and it is the only thing that revokes.** Dropping somebody's
    access means rotating the key they hold and re-issuing the new one to everyone else.

    The list of who "everyone else" is comes from the **account roster** — each user's
    `public_key`, registered in `users.json` (`users set-keys`). It used to be implicit
    in the shared enc-key file: every authorised key was in it, so a rekey re-wrapped what it
    found. With one file per machine there is nothing central to read, so the registry is
    explicit — and it holds only *public* keys, which is why losing it costs nothing but a
    round of re-registration.

    Each holder is sent their own payload through the message spool, exactly as
    `user-authorize` does; they run `msg act` on it to take it. An account with no registered
    public key cannot be re-issued to and is named, not skipped silently — that person loses
    access at this rotation, which is sometimes the intent and must never be a surprise.
    `users set-keys` fills the registry from what every holder already has.

    Because the git filter is deterministic, every committed blob depends on the master key, so
    a rotation re-encrypts the tracked private files via `git add --renormalize`.
    """
    from solver.web.msg.notify import notify_user
    try:
        read_master_key()  # proof of authority: must currently hold and verify the master key
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] refusing to rekey -- current key check failed ({exc})')
        return 1
    holders = registered_public_keys()
    if holders is None:
        console.print('[error]error:[/error] could not read the account roster — rekey needs it to '
                      'know who to re-issue to (is euler-auth.service running, and can you sudo?)')
        return 1
    mine = public_key_hex(load_private_key().public_key())
    named, unregistered = {i: k for i, k in holders.items() if k}, [i for i, k in holders.items() if not k]
    console.print(f'[primary]re-issuing to {len(named)} registered public key(s)[/primary]')
    for identity in unregistered:
        console.print(f'  [warning]{identity}[/warning] has no registered public key — they LOSE '
                      'access at this rotation (`users set-keys` first to keep them)')
    if not sure(f'Rotate the master key, re-encrypt all private files, and re-issue to '
                f'{len(named)} holder(s)? Anyone without a registered public key loses access.',
                phrase='rekey'):
        raise Abort('rekey cancelled')

    new_master: bytes = token_bytes(32)
    # Ourselves first: a rotation that fails half way must still leave THIS machine able to
    # decrypt, or the operator has locked themselves out of the tree they just re-encrypted.
    write_enc_key_file(enc_key_payload(load_private_key().public_key(), new_master))
    console.print(f'[success]master key rotated[/success] [muted]({config["enc_key_file"]})[/muted]')
    if (landed := _land_reencrypted_blobs()) != 0:
        return landed
    for identity, public_key in named.items():
        if public_key == mine:
            continue
        pub = X25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
        sent = notify_user(identity, f'{KEY_ISSUE_SUBJECT}rotated master key',
                           _issue_body(enc_key_payload(pub, new_master)))
        console.print(f'  {"sent to" if sent else "COULD NOT REACH"} [accent]{identity}[/accent]')
    console.print('[success]Rotated, published, and issued.[/success]')
    return 0


def _land_reencrypted_blobs() -> int:
    """Re-encrypt the tracked private files under the new key and get them onto origin.

    **This must finish before anybody is issued the new key**, and that ordering is the whole
    point of the function. A rotation makes every blob committed before it unreadable, so a
    holder who saves the new key while the re-encrypted tree is still sitting in the operator's
    worktree is stranded: their own HEAD no longer opens, which means no checkout, no stash and
    therefore no merge — they cannot even sync their way out. Publishing first makes the window
    zero-width; a clone that saves the key always has somewhere to land.

    Only `solutions/private` is committed, by pathspec. `git commit` otherwise commits the
    whole index, and a rotation that swept an operator's unrelated staged work into a commit
    labelled as re-encryption has happened here before.

    A failed push is fatal to the rotation: returning non-zero leaves the keys unissued, so the
    operator can fix the remote and run `key-rekey` again. The second run mints a further key —
    which costs nothing, because nobody ever received this one.
    """
    console.print('[muted]Re-encrypting tracked private files...[/muted]')
    root = config['root_dir']
    run(['git', 'add', '--renormalize', '--', 'solutions/private'], cwd=root, check=False)
    staged = run(['git', 'diff', '--cached', '--name-only', '--', 'solutions/private'],
                 cwd=root, capture_output=True, text=True).stdout.split()
    if not staged:
        console.print('[muted]No tracked private files changed — nothing to publish.[/muted]')
        return 0
    console.print(f'[muted]committing [accent]{len(staged)}[/accent] re-encrypted blob(s)[/muted]')
    message = (f'chore(crypto): re-encrypt private solutions under the rotated master key\n\n'
               f'{len(staged)} blob(s) renormalised by `key-rekey`. Every commit before this one '
               f'is encrypted under the retired key.\n')
    if run(['git', 'commit', '-m', message, '--', 'solutions/private'],
           cwd=root, check=False).returncode != 0:
        console.print('[error]error:[/error] the re-encrypted blobs would not commit — '
                      'keys NOT issued. Fix the commit, then run `key-rekey` again.')
        return 1
    if run(['git', 'push', 'origin', 'HEAD:master'], cwd=root, check=False).returncode != 0:
        console.print('[error]error:[/error] the re-encrypted blobs would not reach origin — '
                      'keys NOT issued, because a holder who saved one now could not sync to a '
                      'tree their key opens. Push, then run `key-rekey` again.')
        return 1
    console.print('[success]re-encrypted tree published to origin/master[/success]')
    return 0


def _resolve_key_request(thread_id: str) -> tuple[str, str] | None:
    """Read a key-authorization thread and return `(public_key, identity)`, or None.

    The identity comes from the thread's **author**, not from its text: the spool resolved
    that box from `SO_PEERCRED` when the request was filed, so it is the one field in a
    message a sender cannot dress up as somebody else. Only the key itself is read out of
    the body, under rules that refuse rather than guess:

    - the subject must be the one `_request_authorization` files under, so an arbitrary
      `msg send` is never mined for hex;
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
    if not str(thread.get('subject', '')).startswith(KEY_REQUEST_SUBJECT):
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


@register(requires='maintainer', aliases=('authorize',))
def user_authorize(target: str, identity: str = '') -> int:
    """Wrap the master key for someone else and send it to them.

    *target* is either form of the same act, told apart by shape:

    - a **16-hex message id** — the key-authorization request their `user` command filed
      (`msg list` shows them). The key and the requester come from that message, the grant
      is confirmed, the payload is sent as **its own message** for them to `msg act` on, and
      the request is dismissed — it is worked, and a queue that keeps worked requests is a
      queue nobody trusts;
    - a **64-hex public key** — the same act by hand, for a key that reached you some other
      way. *identity* names who to send it to.

    **Nothing is written to a shared file, because there is no shared file.** The payload is
    the whole of the recipient's enc-key file — `verify` plus the master key wrapped to their
    public key — and it travels through the spool for the same reason the old tracked file
    could sit in a public repo: without their private key it is inert. They run `msg act` on it
    to take it; until they do, nothing has changed for them.

    The public key is also registered on their account (as `users set-keys` does in bulk),
    which is what `key-rekey` reads when it re-issues a rotated key. Best-effort: it needs
    the admin plane, so from a web shell it prints the command for the operator instead of
    failing the grant. Aliased as `authorize`.

    Args:
        target: The 16-hex id of a key-authorization message, or a 64-hex public key.
        identity: Who the key belongs to. Taken from the thread for the message form;
            required for the bare-key form, where there is nobody to send it to otherwise.
    """
    from solver.web.msg.notify import dismiss_thread, notify_user
    token = target.strip().lower()
    thread_id = ''
    if _THREAD_ID_RE.fullmatch(token):
        resolved = _resolve_key_request(token)
        if resolved is None:
            return 1
        thread_id, public_key, identity = token, resolved[0], resolved[1]
    elif _PUBLIC_KEY_RE.fullmatch(token):
        public_key = token
        if not identity:
            console.print('[error]error:[/error] a bare public key needs an identity — there is '
                          'nobody to send the key to otherwise')
            return 1
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

    console.print(f'[primary]issuing to:[/primary] {identity}\n'
                  f'[primary]public key:[/primary] {public_key}')
    if not sure('Send this key the master key?', phrase='send'):
        raise Abort('not sent')

    # Its own message, always. There are no replies: a grant hidden inside the request it
    # answers is invisible to everything that reads the request, and `msg act` would have
    # to go looking for it.
    delivered = notify_user(identity, f'{KEY_ISSUE_SUBJECT}{identity}',
                            _issue_body(enc_key_payload(pub, master_key)))
    if not delivered:
        console.print('[error]error:[/error] could not deliver the key — nothing was sent. '
                      'Check the message spool and retry.')
        return 1
    console.print(f'[success]Sent to [accent]{identity}[/accent].[/success] '
                  '[muted]They run `msg act <id>` to take it.[/muted]')
    if thread_id and not dismiss_thread(thread_id):
        # The grant is delivered either way; an undismissed request is only clutter, and
        # saying so beats a silent one that reappears in the queue tomorrow looking unworked.
        console.print(f'[muted]Could not dismiss the request [accent]{thread_id}[/accent] — '
                      '`msg dismiss` it yourself.[/muted]')
    _register_public_key(identity, public_key)
    return 0


def save_issued_key(body: str) -> bool:
    """Take the enc-key payload out of an issue message and write it — verified first.

    An issued key is always its own message, so there is one body to read and one payload in
    it. Proving it is the whole gate: it must unwrap with **this machine's** private key and
    its `verify` must decrypt to the known text. A payload wrapped to somebody else, or
    corrupted in transit, fails here — before the write, because the file it replaces may be
    the only thing between this machine and the whole private tree.
    """
    try:
        private_key = load_private_key()
    except (FileNotFoundError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot read your private key ({exc}); run `user`')
        return False
    mine = public_key_hex(private_key.public_key())
    match = _JSON_OBJECT_RE.search(body)
    if match is None:
        console.print('[error]error:[/error] no key payload found in that message')
        return False
    try:
        payload = {str(k): str(v) for k, v in loads(match.group(0)).items()}
    except (ValueError, AttributeError, TypeError):
        console.print('[error]error:[/error] the key payload in that message is not readable')
        return False
    if mine not in payload:
        console.print(f'[error]error:[/error] that key was issued to a different public key — '
                      f'yours is [accent]{mine}[/accent]. Ask for it to be re-issued.')
        return False
    try:
        master_key = unlock(private_key, payload[mine])
    except InvalidTag:
        console.print('[error]error:[/error] the payload does not unwrap with your private key')
        return False
    if not verify_master_key(payload, master_key):
        console.print('[error]error:[/error] the payload fails verification — nothing written')
        return False
    # Last moment at which the key that opens HEAD is still the key in place. If this payload
    # is a rotation, everything committed becomes unreadable one line down, and with it any way
    # of telling which private files carry local edits — so ask now, and hand the answer on.
    from solver.core.git import enc_key_arrived, private_local_edits
    local_edits = private_local_edits()
    write_enc_key_file(payload)
    console.print(f'[success]Master key saved[/success] [muted]({config["enc_key_file"]})[/muted]')
    enc_key_arrived(local_edits)
    return True


def _issue_body(payload: dict[str, str]) -> str:
    """The message body carrying an enc-key payload — a line of prose, then the JSON.

    `msg act` reads the JSON object out of it, so the prose above is free to change and the
    braces are the contract. Kept human-readable on purpose: the recipient sees what arrived
    and what to do with it, not an opaque blob.
    """
    return ('Your master-key access. Run `msg act <id of this message>` to write it to '
            'your enc-key file; the private solutions decrypt in place once you do.\n\n'
            + dumps(payload, indent=2) + '\n')


def _register_public_key(identity: str, public_key: str) -> None:
    """Record *public_key* on the account, best-effort — the registry `key-rekey` reads.

    It needs the auth admin plane, which needs sudo, which a web shell cannot get. Rather
    than fail a grant that has already been delivered, print the one command that finishes
    the job. A missing registration costs nothing until the next rotation, when it costs
    that person their access — which is why `key-rekey` names them rather than skipping on.
    """
    from solver.web.auth.commands import register_public_key
    if register_public_key(identity, public_key):
        return
    console.print('[muted]Not registered for rekey (needs sudo). From the operator\'s terminal: '
                  '[accent]users set-keys[/accent] — it sweeps everyone.[/muted]')


# ==================================================================================================================== #
#                                               user identity
# ==================================================================================================================== #
@register(requires='reader')
def user(regen: bool = False) -> int:
    """Show the solver user, the current identity, and whether it can decrypt.

    A key pair is created only when the identity file is **truly absent** (first run) or on
    an explicitly confirmed `--regen`. An id file that *exists but cannot be read* — the
    vault is locked, the session key is stale, the vault file was lost — is a **vault
    failure to fix, never a reason to mint a new identity**: replacing the key would
    silently orphan the real one, and with it any enc-key authorization it carries.

    Args:
        regen: Replace the existing key pair with a fresh one, after confirmation, and
            re-wrap the master key to it. Defaults to False.
    """
    app_user = app_config['subject']
    console.print(f'[primary]solver user:[/primary] {app_user.user} [muted]({app_user.profile})[/muted]')
    id_file: Path = config['private_key_file']
    private_key: X25519PrivateKey | None = None
    minted: bool = False  # a key was created here — the only path that files a request
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
            if not sure('REPLACE the unreadable identity with a fresh key pair? The old file is '
                        'kept as a rotated backup, but any enc-key access it had is lost.',
                        phrase='replace'):
                raise Abort('keeping the existing (unreadable) identity file')
    if regen and private_key is not None and not sure('Replace the existing private key with a '
                                                      'new one?', phrase='replace'):
        console.print('[muted]Keeping the existing private key.[/muted]')
        regen = False
    if regen or private_key is None:
        # Capture the master key with the OUTGOING key before replacing it. Whether that
        # succeeds is the whole decision below: hold it, and the rotation is self-service —
        # re-wrap to the new key and you are done, because the enc-key file is this machine's
        # and nobody else's copy has to agree. Fail, and there is nothing to carry, so the
        # new key needs issuing by somebody who does hold it.
        carry: bytes | None = None
        try:
            carry = read_master_key()
        except (FileNotFoundError, KeyError, ValueError):
            carry = None
        try:
            private_key = _create_user_key()
        except PermissionError:
            # A vault that exists but is locked: the persist refused, so nothing was minted
            # and nothing was lost. It must NOT reach the request path below — a locked vault
            # is not missing access, and filing a key request for someone who already has the
            # master key has staff re-issuing for nothing.
            return 1
        if carry is not None:
            write_enc_key_file(enc_key_payload(private_key.public_key(), carry))
            console.print('[success]Master-key access carried to the new key[/success] '
                          f'[muted]({config["enc_key_file"]})[/muted]')
        # A new identity is exactly what the account page's public-key panel shows —
        # nudge it to re-read (a no-op unless it is the visible pane). Only when a key
        # was actually minted: a bare `user` status view changed nothing.
        osc.account_changed()
        minted = True
    pub: str = public_key_hex(private_key.public_key())
    # It must answer for the key material as it is NOW. `read_master_key` is
    # lru_cached, and a web shell is long-lived: without this, `user` in a shell that read
    # the key successfully an hour ago reports "✓ can encrypt/decrypt" from that cache while
    # every fresh process — the git filter above all — fails. This command exists to say
    # where you stand, so it is the one place the cache must not be allowed to answer.
    read_master_key.cache_clear()
    try:
        read_master_key()
        console.print(f'[primary]public key:[/primary] {pub}\n[success]✓ can encrypt/decrypt[/success]')
    except (FileNotFoundError, KeyError, ValueError):
        # The enc-key file is missing, or holds nothing this key opens. That is the whole
        # test: it does not matter whether this is a first run or a rotation whose carry
        # failed — either way the key needs issuing by somebody who holds the master key.
        console.print(f'[primary]public key:[/primary] {pub}\n[error]✗ cannot encrypt/decrypt[/error]')
        if minted:
            _request_authorization(app_user.user, pub)
        else:
            console.print('[muted]Ask a maintainer to `user-authorize` this public key, or '
                          '`key-reconstruct` from shares.[/muted]')
    return 0


def _request_authorization(identity: str, public_key: str) -> None:
    """File a key-authorization request with staff for a freshly minted key.

    Only on the paths that need it: a key was **just minted** and somebody holding the
    master key has to run `user-authorize` on it before the grant is real anywhere but
    this working tree. A bare `user` status view is not a request, and neither is a mint
    by someone who can authorise it themselves (:func:`_make_the_rotation_durable`).

    One condition reaches here: a key was minted and the master key could not be loaded —
    missing file, or nothing in it this key opens. Whether that is a first run or a rotation
    whose carry failed makes no difference to what has to happen next.

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
        f'{KEY_REQUEST_SUBJECT}{identity}',
        f'{identity} holds a key pair but not the master key, so the private solutions do '
        f'not decrypt for them yet.\n\n'
        f'public key: {public_key}\n\n'
        f'To issue it, run:\n'
        f'    user-authorize <the id of this message>\n')
    if sent:
        console.print('[muted]A key-authorization request has been sent to the maintainers.[/muted]')
    else:
        # The spool is how this reaches staff; when it cannot, say so and hand over the
        # thing they need. Silence here would leave a rotation that nobody is coming to fix.
        console.print('[muted]Could not reach the message spool — send this public key to a '
                      'maintainer yourself.[/muted]')


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
    order is: an existing session key file, then `$EULER_VAULT_PASSWORD` (both handled by
    :func:`~solver.crypto.vault.ensure_session_key`, non-interactively), and only then the
    operator. A shell calls this once at startup; children -- notably the git filter, which has
    no terminal and cannot be asked anything -- inherit the key file it materialises.

    Any key file this call *creates* is removed at process exit (:func:`_own_key_file`); one it
    merely found is left alone, because it belongs to whoever wrote it.

    Returns the `VK`, or None when there is no vault, when the vault stays locked, or when
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
    if not (interactive and dialogue.interactive()):
        return None
    try:
        password: str = dialogue.secret('Vault password', hint=f'set ${config["vault_password_env"]}')
    except Abort:
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
    """Prompt for a password twice (hidden); return it, or None when the two do not match."""
    try:
        return dialogue.secret(prompt, confirm_twice=True)
    except Abort as abort:
        console.print(f'[error]error:[/error] {abort.message}')
        return None


def _orphaned_vault_files() -> list[str]:
    """Vault-encrypted secret files with NO vault file to unwrap their key — a broken state.

    Their `VK` is unrecoverable without `~/.euler/vault`, so they are unreadable by
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


@register(requires='reader')
def vault(action: Literal['status', 'init', 'unlock', 'change-password'] = 'status') -> int:
    """Encrypt this user's `id` + `env` at rest under a password-derived vault key.

    - `status` (default): show whether the vault exists, which secret files are encrypted, and
      whether this session can decrypt them.
    - `init`: create the vault and migrate the existing plaintext `id`/`env` into it in place, then
      unlock the current session. Prompts for a new password.
    - `unlock`: unlock a locked session (the shell asks at startup; this is the retry — after a
      typo, or once you have the password to hand).
    - `change-password`: re-wrap the vault key under a new password (the secrets are not
      re-encrypted).

    The password is never stored: set `$EULER_VAULT_PASSWORD` for a non-interactive unlock
    (a script, CI), otherwise you are asked once per shell.

    Args:
        action: Which of the four operations above to run. Defaults to 'status'.
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
    current: str = dialogue.secret('Current vault password')
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


def _share_shape(share: str) -> str | None:
    """Reject a mistyped share as it is entered, rather than after the last one."""
    if not re.fullmatch(r'[0-9a-fA-F]+', share):
        return 'a share is hexadecimal — check for a stray character'
    if len(share) != 2 * _HEX_WIDTH:
        return f'a share is {2 * _HEX_WIDTH} hex characters, this one is {len(share)}'
    return None


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


@register(requires='admin')
def key_split(num_shares: int = 3, threshold: int = 2) -> int:
    """Print Shamir shares of the current master key.

    Any `threshold` of the printed shares reconstruct the key through `key-reconstruct`;
    fewer reveal nothing. Store them apart from each other.

    Args:
        num_shares: How many shares to print. Defaults to 3.
        threshold: How many of them are needed to reconstruct the key. Must be at least 2
            and no more than `num_shares`. Defaults to 2.
    """
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


@register(requires='reader')
def key_reconstruct(threshold: int = 2) -> int:
    """Reconstruct the master key from Shamir shares and store it for this user.

    Prompts for the shares one at a time, reconstructs the key, and writes it wrapped to
    this holder's public key — the recovery path when no `user-authorize` grant is coming.
    Needs a private key already in place: run `user` first.

    Args:
        threshold: How many shares to ask for — the threshold the shares were split at.
            Defaults to 2.
    """
    try:
        private_key: X25519PrivateKey = load_private_key()
    except (FileNotFoundError, ValueError) as exc:
        console.print(f'[error]error:[/error] need a private key first ({exc}); run `user`')
        return 1
    shares: list[str] = [
        text(f'Master key share {i} of {threshold}', validate=_share_shape)
        for i in range(1, threshold + 1)
    ]
    try:
        master_key: bytes = _reconstruct_secret(shares)
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    # Check the reconstruction against the file we already have, when there is one: the
    # shares are typed by hand, and writing an unverified key over a working one would trade
    # a recovery for a lock-out.
    if config['enc_key_file'].exists():
        existing: dict[str, Any] = read_enc_key_file()
        if config['enc_key_verify'] in existing and not verify_master_key(existing, master_key):
            console.print('[error]error:[/error] reconstructed key fails verification; wrong shares?')
            return 1
    write_enc_key_file(enc_key_payload(private_key.public_key(), master_key))
    console.print(f'[success]Master key reconstructed from {threshold} shares and stored.[/success]')
    return 0
