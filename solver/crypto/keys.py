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
  it to another public key, or split it in half. Issuing goes through the message spool
  (`user-authorize` sends, `msg act` writes); a rotation of one's own key pair needs nobody.

Granting it to somebody is one act with two halves. `user-authorize` records their **public
key** in the roster (`/etc/euler/roster/users.json`, :mod:`solver.auth.roster`) and delivers half
the master key, sealed to that key; the other half is this machine's `share_file`, which every
uid on the host can read and only the operator writes. `key-reconstruct` puts the two together
at their end. So no single artefact is ever the key — the message, the private key that opens
it, and access to the host all count — and `key-split` is the same delivery without the
request-thread handling, plus the run that lays the local half down in the first place.

**Off the host** there is no shared half to complete, so the pair is `host-authorize` (seal the
whole master key to a public key and mail it) and `host-unlock` (take the mailed block and
install it). Two commands rather than one because the two ends are two machines.

The non-interactive primitives (load, lock/unlock, encrypt/decrypt) come from `solver.crypto.ciphers`
the file locations from `solver.config` and the wire format from `solver.crypto.wire`; this module
never re-implements them. The git
filter (`solver.crypto.gitfilter`) does not import this module.

Shell commands registered here: `user`, `vault`, `key-rekey`, `user-authorize`, `key-split`,
`key-reconstruct`, `host-authorize`, `host-unlock`.
"""
from __future__ import annotations

__all__ = ['host_authorize', 'host_unlock', 'key_reconstruct', 'key_rekey', 'key_split',
           'read_local_share', 'save_issued_key', 'share_in_message', 'unlock_session', 'user',
           'user_authorize', 'vault', 'write_enc_key_file']

import atexit
import os
import re
from datetime import datetime, timezone
from json import dumps, loads
from pathlib import Path
from secrets import randbelow, token_bytes
from subprocess import run
from tempfile import NamedTemporaryFile
from typing import Annotated, Any, Literal

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.auth import roster
from solver.config import ExitCodes, config as app_config
from solver.crypto import wire
from solver.core import osc
from solver.crypto import vault as vault_mod
from solver.crypto.ciphers import (enc_key_payload, encrypt_blob, load_private_key, lock,
                                   public_key_hex, read_enc_key_file, read_master_key, unlock,
                                   verify_master_key)
from solver.shell import console, register
from solver.shell import dialogue
from solver.shell.dialogue import Abort, Ask, Choice, sure
from solver.shell.variables import variable
from solver.web.auth.commands import registered_public_keys
from solver.web.msg import KEY_ISSUE_SUBJECT, KEY_REQUEST_SUBJECT, KEY_SHARE_SUBJECT

#: A public key on the wire and in the enc-key file: 32 bytes of lowercase hex.
_PUBLIC_KEY_RE = re.compile(r'\b[0-9a-f]{64}\b')

#: Share-shaped hex on the wire: the 262-digit share itself (two 131-digit fields, `x` and
#: `f(x)` — see `_share_text`), or the longer blob it becomes once wrapped to a public key.
#: One pattern for both, so the message body needs no marker saying which it carries and
#: `_unwrap_share` decides by shape.
_SHARE_RE = re.compile(r'\b[0-9a-f]{262,}\b')

#: The JSON object an issue message carries — the payload, wherever it sits in the prose.
_JSON_OBJECT_RE = re.compile(r'\{.*\}', re.DOTALL)

#: A spool thread id (`secrets.token_hex(8)`) — half a public key's length, which is what
#: lets `user-authorize` take either without a flag to say which it was given.
_THREAD_ID_RE = re.compile(r'[0-9a-f]{16}')

#: The markers around a mailed master key (`host-authorize` writes them, a person reads them).
_BLOCK_BEGIN: str = '----- BEGIN EULER MASTER KEY -----'
_BLOCK_END: str = '----- END EULER MASTER KEY -----'

#: The loopback mail relay, as `auth.env` sets it for the service — repeated here because the
#: operator's terminal cannot read that file (`root:euler-auth 0640`) and needs no secret to
#: submit: the relay holds the credentials, and the firewall decides who may reach it.
_SMTP_RELAY: str = os.environ.get('EULER_SMTP_RELAY', '127.0.0.1:8025')


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
    keep: int = app_config.private_key_backups
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
    key_file: Path = app_config.private_key_file
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
    enc_file: Path = app_config.enc_key_file
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

    The list of who "everyone else" is comes from the **roster** — each holder's `public_key`
    in `/etc/euler/roster/users.json`, written by the grant that issued to them. It used to be
    implicit in the shared enc-key file: every authorised key was in it, so a rekey re-wrapped
    what it found. With one file per machine there is nothing central to read, so the registry
    is explicit — and it holds only *public* keys, which is why losing it costs nothing but a
    round of re-authorization.

    Each holder is sent their own payload through the message spool, exactly as
    `user-authorize` does; they run `msg act` on it to take it. An account with no registered
    public key cannot be re-issued to and is named, not skipped silently — that person loses
    access at this rotation, which is sometimes the intent and must never be a surprise.

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
        console.print('[error]error:[/error] could not read the roster — rekey needs it to know who '
                      f'to re-issue to (is [accent]{_share_label()}[/accent] present and readable?)')
        return 1
    mine = public_key_hex(load_private_key().public_key())
    named, unregistered = {i: k for i, k in holders.items() if k}, [i for i, k in holders.items() if not k]
    console.print(f'[primary]re-issuing to {len(named)} registered public key(s)[/primary]')
    for identity in unregistered:
        console.print(f'  [warning]{identity}[/warning] has no registered public key — they LOSE '
                      'access at this rotation — authorise them first to keep them)')
    if not sure(f'Rotate the master key, re-encrypt all private files, and re-issue to '
                f'{len(named)} holder(s)? Anyone without a registered public key loses access.',
                phrase='rekey'):
        raise Abort('rekey cancelled')

    new_master: bytes = token_bytes(32)
    # Ourselves first: a rotation that fails half way must still leave THIS machine able to
    # decrypt, or the operator has locked themselves out of the tree they just re-encrypted.
    write_enc_key_file(enc_key_payload(load_private_key().public_key(), new_master))
    console.print(f'[success]master key rotated[/success] [muted]({app_config.enc_key_file})[/muted]')
    # The local half follows the key it belongs to. One drawn against the retired key would
    # still *work* — any point plus a secret determines a line — so leaving it would mean
    # `key-split` quietly completing halves against a key that opens nothing, and the holder
    # discovering the rotation at the far end. Redrawn only where the split path is already in
    # use: a machine with no share does not gain one from a rotation.
    if read_local_share() is not None:
        _write_local_share(new_master)
        console.print('[success]local key share redrawn against the new key[/success] '
                      f'[muted]({_share_label()})[/muted]')
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
    labelled as re-encryption has happened here before. The redrawn share is **not** part of
    this: it is operational state on the host, not repository content, so it never enters a
    commit at all.

    A failed push is fatal to the rotation: returning non-zero leaves the keys unissued, so the
    operator can fix the remote and run `key-rekey` again. The second run mints a further key —
    which costs nothing, because nobody ever received this one.
    """
    console.print('[muted]Re-encrypting tracked private files...[/muted]')
    root = app_config.root_dir
    paths = ['solutions/private']
    run(['git', 'add', '--renormalize', '--', *paths], cwd=root, check=False)
    staged = run(['git', 'diff', '--cached', '--name-only', '--', *paths],
                 cwd=root, capture_output=True, text=True).stdout.split()
    if not staged:
        console.print('[muted]No tracked private files changed — nothing to publish.[/muted]')
        return 0
    console.print(f'[muted]committing [accent]{len(staged)}[/accent] re-encrypted blob(s)[/muted]')
    message = (f'chore(crypto): re-encrypt private solutions under the rotated master key\n\n'
               f'{len(staged)} blob(s) renormalised by `key-rekey`. Every commit before this one '
               f'is encrypted under the retired key.\n')
    if run(['git', 'commit', '-m', message, '--', *paths],
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
    """Record someone's public key and send them half the master key.

    *target* is either form of the same act, told apart by shape:

    - a **16-hex message id** — the key-authorization request their `user` command filed
      (`msg list` shows them). The key and the requester come from that message, the grant
      is confirmed, the half is sent as **its own message** for them to `msg act` on, and the
      request is dismissed — it is worked, and a queue that keeps worked requests is a queue
      nobody trusts;
    - a **64-hex public key** — the same act by hand, for a key that reached you some other
      way. *identity* names who to send it to.

    Two things happen, and the first is the durable one. The public key is written to the
    **roster** (`/etc/euler/roster/users.json`), which is what a later rotation re-issues
    against and what every shell — terminal or web — can read without `sudo`. Then delivery goes
    through `key-split`: half the master key, sealed to that public key, against the half the
    repository already carries. So a grant is never one artefact — the message, the private
    key that opens it and a current clone are all needed, and the recipient's own
    `key-reconstruct` proves the result before it writes anything.

    That is why this needs the repository's half to be **committed and pushed first**: it
    refuses rather than sending a half nobody can complete. `key-split` on its own lays that
    half down. Aliased as `authorize`.

    Args:
        target: The 16-hex id of a key-authorization message, or a 64-hex public key.
        identity: Who the key belongs to. Taken from the thread for the message form;
            required for the bare-key form, where there is nobody to send it to otherwise.
    """
    from solver.web.msg.notify import dismiss_thread
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
    if _public_key_from(public_key) is None:
        return 1

    # The repository's half has to be current *before* anything is sent, and this is the one
    # place that cannot be discovered at the far end: `key-split` would lay a fresh half and
    # report success without sending, and the request would then be dismissed as worked.
    if not _local_share_ready():
        console.print('[error]error:[/error] the repository has no current half of the master '
                      f'key ([accent]{_share_label()}[/accent]). Run [accent]key-split[/accent] '
                      'to lay one down, commit and push it, then authorise again.')
        return 1

    # The key first, the delivery second. A recorded key with no message costs a re-send; a
    # message with no recorded key costs that person their access at the next rotation.
    roster.upsert(identity, public_key=public_key)
    if (sent := key_split(identity, public_key)) != 0:
        return sent
    if thread_id and not dismiss_thread(thread_id):
        # The grant is delivered either way; an undismissed request is only clutter, and
        # saying so beats a silent one that reappears in the queue tomorrow looking unworked.
        console.print(f'[muted]Could not dismiss the request [accent]{thread_id}[/accent] — '
                      '`msg dismiss` it yourself.[/muted]')
    return 0


@register(requires='admin')
def host_authorize(public_key: Annotated[str, Ask('The public key of the machine to authorize')] = '',
                   email: Annotated[str, Ask('Which address should it be mailed to?')] = '') -> int:
    """Mail the master key, sealed to one machine's public key — the off-host grant.

    `key-split` needs both halves to be reachable: the sealed message, and the half sitting on
    this host. A machine that is not *on* this host has no second half, so there is nothing to
    complete — and the spool cannot reach it either. This is that case, and it trades the
    split's third factor for a channel that actually arrives: the whole master key, sealed to
    the machine's public key so it is inert to the mail provider and to every mailbox it
    passes through, delivered by e-mail with a marked block to copy.

    The far end runs `host-unlock` and pastes the block. Nothing is recorded here and nothing
    is registered: an off-host machine has no account, no slug and no instance — which is why
    this asks for a public key rather than an identity.

    Mail is submitted through the loopback relay from **this terminal**, which the egress
    firewall permits for the operator's uid and bars for every per-user one. When the relay
    cannot be reached the block is printed instead, so the grant is never lost to a mail
    problem — send it yourself, by any channel you trust.

    Args:
        public_key: [asked] The 64-hex X25519 public key of the machine being authorized —
            what `user` prints there.
        email: [asked] Where to send it. Their address, or your own if you intend to forward
            it by another route.
    """
    if not public_key or not email:
        raise Abort('host-authorize needs a public key and an address', rc=ExitCodes.EXIT_USAGE)
    recipient: X25519PublicKey | None = _public_key_from(public_key.strip().lower())
    if recipient is None:
        return 1
    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    console.print(f'[primary]sealing the master key to:[/primary] {public_key_hex(recipient)}\n'
                  f'[primary]mailing it to:[/primary] {email}')
    if not sure('Whoever holds the private key for that public key can then decrypt every '
                'private solution, with nothing else needed. Send it?', phrase='send'):
        raise Abort('not sent')
    block: str = _sealed_block(enc_key_payload(recipient, master_key))
    from solver.web.auth.mail import Mailer
    try:
        Mailer(_SMTP_RELAY, app_config.base_url).send_master_key(email, block)
    except OSError as exc:
        # Never a lost grant: the payload is already sealed and safe to display, so print it
        # and let the operator carry it. A relay that is down, absent (a dev box), or barred
        # to this uid all land here, and all have the same answer.
        console.print(f'[warning]could not reach the mail relay ({exc})[/warning] — '
                      'send this yourself:\n')
        console.print(block, markup=False, highlight=False)
        return 1
    console.print(f'[success]Sent to [accent]{email}[/accent].[/success] '
                  '[muted]They run `host-unlock` and paste the block.[/muted]')
    return 0


@register(requires='admin')
def host_unlock(payload: Annotated[str, Ask('Paste the block from the mail', multiline=True)] = '') -> int:
    """Take the mailed block from `host-authorize` and unlock this machine.

    The receiving half of the off-host grant, and the same proof as every other way in: the
    payload must unwrap with **this machine's** private key and its `verify` must decrypt to
    the known text. Only then does it replace what is here — the file it overwrites may be the
    only thing between this machine and the whole private tree, so a bad or mistargeted block
    has to fail before the write, not be discovered after it.

    Paste everything between the markers; the surrounding prose is ignored, and so is whatever
    the mail client did to the line breaks.

    Args:
        payload: [asked] The block from the mail. Asked for over several lines when it is not
            given — end with a blank line.
    """
    if not payload:
        raise Abort('host-unlock needs the block from the mail', rc=ExitCodes.EXIT_USAGE)
    if not save_issued_key(payload):
        return 1
    console.print('[muted]The private solutions decrypt in place from here — `git-sync` if this '
                  'clone is behind.[/muted]')
    return 0


def _sealed_block(payload: dict[str, str]) -> str:
    """The copy-this block a sealed key travels in.

    Markers rather than bare JSON because this crosses a mail client, which wraps lines, adds
    quote prefixes on a reply, and sometimes helpfully "corrects" punctuation. The reader on
    the far end is :func:`save_issued_key`, which finds the JSON object inside whatever it is
    given — so the markers are for the human deciding what to copy, and the braces remain the
    machine's contract.
    """
    return (f'{_BLOCK_BEGIN}\n{dumps(payload, indent=2)}\n{_BLOCK_END}\n')


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
    console.print(f'[success]Master key saved[/success] [muted]({app_config.enc_key_file})[/muted]')
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
    app_user = app_config.subject
    console.print(f'[primary]solver user:[/primary] {app_user.user} [muted]({app_user.profile})[/muted]')
    id_file: Path = app_config.private_key_file
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
                          f'[muted]({app_config.enc_key_file})[/muted]')
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
    before: str = os.environ.get(wire.VAULT_KEY_ENV, '')
    if (vault_key := vault_mod.ensure_session_key()) is not None:
        after: str = os.environ.get(wire.VAULT_KEY_ENV, '')
        if after and after != before:
            _own_key_file(Path(after))
        return vault_key
    if not (interactive and dialogue.interactive()):
        return None
    try:
        password: str = dialogue.secret('Vault password', hint=f'set ${wire.VAULT_PASSWORD_ENV}')
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
    return [p.name for p in (app_config.private_key_file, app_config.env_file)
            if p.exists() and vault_mod.is_vault_encrypted(p.read_bytes())]


def _vault_status() -> int:
    """Report whether the vault exists, the state of each secret file, and whether this
    session's key actually decrypts them (a stale/foreign key is flagged, not hidden)."""
    id_file: Path = app_config.private_key_file
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
    if os.environ.get(wire.VAULT_PASSWORD_ENV):
        console.print('[warning]note:[/warning] [accent]$'
                      f'{wire.VAULT_PASSWORD_ENV}[/accent] still holds the OLD password — '
                      'update it wherever it is set, or the next non-interactive unlock fails.')
    return 0


# ==================================================================================================================== #
#                                       2 of 2 secret sharing (Shamir over GF(2**521-1))
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


def _share_text(x: int, y: int) -> str:
    """One share on the wire: the point `(x, f(x))` as two fixed-width hex fields."""
    return f'{x:0{_HEX_WIDTH}x}{y:0{_HEX_WIDTH}x}'


def _share_point(share: str) -> tuple[int, int]:
    """The `(x, f(x))` a share carries.

    Raises:
        ValueError: If it is not a share — wrong length, or not hexadecimal.
    """
    if len(share) != 2 * _HEX_WIDTH:
        raise ValueError(f'share must be {2 * _HEX_WIDTH} hex chars, got {len(share)}')
    return int(share[:_HEX_WIDTH], 16), int(share[_HEX_WIDTH:], 16)


def _random_share() -> str:
    """A fresh share of *any* secret — the half that lives in the repository.

    It takes no key, and that is not a shortcut: at a threshold of two the shares of a secret
    are one uniformly random point plus the point the line through it and the secret demands.
    Whichever half is drawn first is therefore just a random point, independent of the secret
    — which is what makes it safe to commit, and what lets :func:`_counterpart` mint the other
    half against **whatever the master key is at that moment**.

    `x` is never 0: that is where the secret itself sits.
    """
    return _share_text(randbelow(_PRIME - 1) + 1, randbelow(_PRIME))


def _counterpart(secret: bytes, share: str) -> str:
    """The share that completes *share* into *secret* — the half that travels by message.

    Two points determine the line, one of which is `(0, secret)`: so with the repository's
    share fixed, the second is a free choice of `x` on the line through those two. A fresh `x`
    every time, so the same repository share can be completed for every holder without any of
    them receiving the same second half.

    Raises:
        ValueError: If *secret* is not 32 bytes, or *share* is not a usable share.
    """
    if len(secret) != _SECRET_BYTES:
        raise ValueError(f'secret must be exactly {_SECRET_BYTES} bytes, got {len(secret)}')
    x1, y1 = _share_point(share)
    if x1 % _PRIME == 0:
        raise ValueError('the repository share sits at x = 0, where the secret is — it is not a share')
    intercept: int = int.from_bytes(secret, 'big')
    slope: int = (y1 - intercept) * pow(x1, -1, _PRIME) % _PRIME
    x2: int = x1
    while x2 == x1:                                  # distinct points, or there is no line to draw
        x2 = randbelow(_PRIME - 1) + 1
    return _share_text(x2, _eval_poly([intercept, slope], x2))


def _share_shape(share: str) -> str | None:
    """Reject a mistyped share as it is entered, rather than after the last one."""
    if not re.fullmatch(r'[0-9a-fA-F]+', share):
        return 'a share is hexadecimal — check for a stray character'
    if len(share) != 2 * _HEX_WIDTH:
        return f'a share is {2 * _HEX_WIDTH} hex characters, this one is {len(share)}'
    return None


def _reconstruct_secret(shares: list[str]) -> bytes:
    """Reconstruct the 32-byte key from distinct shares — the repository's half, and one sent."""
    if not shares:
        raise ValueError('need at least one share')
    points: list[tuple[int, int]] = []
    seen: set[int] = set()
    for s in shares:
        x, y = _share_point(s)
        if x in seen:
            raise ValueError(f'duplicate share index {x:x}')
        seen.add(x)
        points.append((x, y))
    secret_int: int = _interpolate_at_zero(points)
    if secret_int.bit_length() > _SECRET_BYTES * 8:
        raise ValueError('reconstructed value out of range; wrong threshold or corrupted shares')
    return secret_int.to_bytes(_SECRET_BYTES, 'big')


# ── the repository's half ───────────────────────────────────────────────────────────────

def read_local_share() -> dict[str, str] | None:
    """This machine's half of the master key and its `verify`, or None when there is no pair.

    Operational state, not repository content: `/etc/euler/share.json` on a deployed host,
    `~/.euler/share.json` on a plain checkout (:func:`solver.config.paths.share_file`).
    It is **read** by everything and written only by the operator, which is what lets a
    maintainer's web shell keep granting without ever needing `sudo`.

    Unreadable counts as absent, deliberately: the answer to a mangled file is to write a
    fresh share, not to fail every path that reads one. What must never be silent is *using*
    a wrong share, and that cannot happen — :func:`key_reconstruct` proves the reconstructed
    key against `verify` before it writes anything.
    """
    try:
        data = {str(k): str(v) for k, v in loads(app_config.share_file.read_text()).items()}
    except (OSError, ValueError, AttributeError, TypeError):
        return None
    return data if _share_shape(data.get('share', '')) is None else None


def _write_local_share(master_key: bytes) -> str:
    """Draw a fresh half of the master key onto this machine and return it.

    The `verify` record is the same fixed-plaintext ciphertext the enc-key file carries, under
    the key this share was drawn for. It is what makes the file self-describing: it dates the
    share to a master key, so `key-split` can tell one that predates a rotation from a current
    one, and `key-reconstruct` can prove a reconstruction on a machine with no enc-key file to
    check against — which is exactly the machine that needs to reconstruct.

    The deployed location is root-owned, so a direct write is tried first and `sudo install`
    is the fallback. Only the operator ever takes this path: everybody else reads.

    Raises:
        PermissionError: If the file cannot be written by either route.
    """
    share: str = _random_share()
    body: str = dumps({'share': share,
                       wire.ENC_KEY_VERIFY: encrypt_blob(wire.VERIFY_TEXT, master_key).hex(),
                       'since': _now_stamp()}, indent=2) + '\n'
    path: Path = app_config.share_file
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        path.chmod(0o644)          # readable by every uid on the host; a share alone is inert
        return share
    except OSError:
        pass
    # A root-owned directory (`/etc/euler`): hand the write to sudo rather than failing at the
    # one act that is the operator's by definition. The temp file is written 0600 in the
    # operator's own space and installed from there, so the payload never sits world-readable
    # anywhere it was not meant to.
    with NamedTemporaryFile('w', suffix='.json', delete=False) as staged:
        staged.write(body)
        staged_path = Path(staged.name)
    staged_path.chmod(0o600)
    try:
        console.print(f'[muted]{path} is root-owned — installing it with sudo.[/muted]')
        done = run(['sudo', 'install', '-m', '0644', '-o', 'root', '-g', 'root',
                    str(staged_path), str(path)], check=False)
    finally:
        staged_path.unlink(missing_ok=True)
    if done.returncode != 0:
        raise PermissionError(f'could not write {path}')
    return share


def _share_label() -> str:
    """The share file as a person should read it — a full path; it is not in the checkout."""
    return str(app_config.share_file)


def _wrap_share(public_key: X25519PublicKey, share: str) -> str:
    """Wrap a share to *public_key* — what actually travels in the message.

    The same envelope an issued key rides in (:func:`~solver.crypto.ciphers.lock`: ephemeral
    X25519 ECDH → HKDF → ChaCha20-Poly1305), applied to the 262-character share text. So the
    two halves of a split are protected by two independent things: the repository half by
    being worth nothing alone, and this half by being readable only to the holder of one
    private key.

    That makes the spool no more trusted than it already had to be. A share in the clear
    would need only a clone to complete — and every collaborator has a clone.
    """
    return lock(public_key, share.encode())


def _unwrap_share(private_key: X25519PrivateKey, token: str) -> str | None:
    """The share inside *token*, or None with the reason already printed.

    Takes either form, told apart by shape, because a share reaches people two ways:

    - a **wrapped blob** — what `key-split` sends. Opened with this machine's private key;
    - a **bare 262-hex share** — one handed over out of band, or typed off another screen.
      Refusing it would make the manual path impossible for the case the manual path exists
      for, and it is no weaker than it looks: whoever can type it already has it.
    """
    if _share_shape(token) is None:
        return token
    try:
        share: str = unlock(private_key, token).decode()
    except (InvalidTag, ValueError, UnicodeDecodeError):
        console.print('[error]error:[/error] that share does not unwrap with your private key — '
                      'it was wrapped to somebody else, or it is corrupt. Ask for it to be re-sent.')
        return None
    if (problem := _share_shape(share)) is not None:
        console.print(f'[error]error:[/error] the payload unwrapped, but {problem}')
        return None
    return share


def _share_body(share: str) -> str:
    """The message body carrying one half of the master key, wrapped to its recipient.

    `msg act` reads the blob out of it (:func:`share_in_message`), so the prose is free to
    change and the run of hex is the contract — exactly as the braces are for an issued key.
    There must be **one** such token in it and no other.
    """
    return ('Half of the master key, sealed to your public key. The other half is already on '
            f'this host ({_share_label()}) — run `msg act <id of this message>` to unwrap this '
            'one, put the two together, and write your enc-key file. The private solutions '
            'decrypt in place once you do.\n\n'
            f'share: {share}\n')


def share_in_message(body: str) -> str | None:
    """The one wrapped share in a `key-split` message, or None with the reason already printed.

    Exactly one, by the same rule `user-authorize` reads a public key under: zero or several
    means this is not the message we know how to work, and key material is not a thing to
    infer from ambiguous text. What comes back is still sealed — only the holder's private
    key opens it (:func:`_unwrap_share`), and this function needs no key at all.
    """
    found = _SHARE_RE.findall(body)
    if len(found) != 1:
        console.print(f'[error]error:[/error] found [accent]{len(found)}[/accent] shares in that '
                      'message; expected exactly one — pass the share to `key-reconstruct` yourself')
        return None
    return str(found[0]).lower()


def _public_key_from(token: str) -> X25519PublicKey | None:
    """*token* as a public key, or None with the reason already printed."""
    if not _PUBLIC_KEY_RE.fullmatch(token):
        console.print('[error]error:[/error] public_key must be 32 bytes of hex')
        return None
    try:
        return X25519PublicKey.from_public_bytes(bytes.fromhex(token))
    except ValueError:
        console.print('[error]error:[/error] that is not a usable X25519 public key')
        return None


def _recipient_key(identity: str, public_key: str) -> X25519PublicKey | None:
    """The public key to seal a share to, or None with the reason already printed.

    Given explicitly it is used as given; otherwise it comes from the **roster**
    (`/etc/euler/roster/users.json`), which is the whole reason that file exists: this lookup
    used to be an admin-plane read behind `sudo`, so the one shell that most needs it — a
    maintainer's web shell, which can never elevate — could not do it at all and had to be
    handed 64 hex characters by hand.

    A key read from the roster is not *trusted*, it is *used*: seal a half to the wrong key and
    the recipient cannot open it, which is a failure at the far end and not a compromise.
    """
    token: str = public_key.strip().lower()
    if not token:
        token = (roster.public_keys().get(roster.slug_of(identity)) or '').strip().lower()
        if not token:
            console.print(f'[error]error:[/error] [accent]{identity}[/accent] has no public key in '
                          f'[accent]{roster.roster_path()}[/accent], so there is nothing to seal their '
                          'half to. They mint one with `user` and are authorised once; or pass '
                          'the key here.')
            return None
    return _public_key_from(token)


@variable('collaborators a sealed share can be sent to')
def holders() -> list[Choice]:
    """Who a share can be sent to — every roster record that has a key to seal it to.

    Read straight from the checkout, so the menu is the same in a terminal and in a web shell.
    Records without a public key are left out rather than offered: `key-split` would refuse
    them a moment later, and a menu must never offer what the command will then refuse.
    Non-strict all the same, so a slug the roster has not caught up with can still be typed.

    `Choice` rather than a type of its own: there is nothing to a holder here but the slug
    and the one thing worth saying about it, so a loop body (`loop {holders}:`) gets
    `{loop.value}` and has everything there is.
    """
    keys = roster.public_keys()
    return [Choice(slug, slug, 'has a public key') for slug in sorted(keys)]


def _local_share_ready() -> bool:
    """Whether this machine holds a half that completes into the **current** master key.

    False covers both "none yet" and "one from before a rotation", because the two lead to
    the same act: lay a fresh one down and commit it before sending anybody anything.
    Exception-safe by construction — it is also read from a dialogue predicate, where a raise
    would take down the command before it could say what was actually wrong.
    """
    try:
        existing = read_local_share()
        return existing is not None and verify_master_key(existing, read_master_key())
    except (FileNotFoundError, KeyError, ValueError):
        return False


def _sends_a_share(_: dict[str, Any]) -> bool:
    """Whether this `key-split` run sends rather than lays the repository's half.

    The laying run sends nothing, so asking it who to send to would be a question with no
    answer — which is what this predicate spares the operator.
    """
    return _local_share_ready()


# ── the commands ────────────────────────────────────────────────────────────────────────

@register(requires='maintainer')
def key_split(identity: Annotated[str, Ask('Who should receive the other half?',
                                           choices='holders', when=_sends_a_share,
                                           strict=False)] = '',
              public_key: str = '') -> int:
    """Send someone half the master key, sealed to their public key.

    Two halves of a 2-of-2 split, and **neither is worth anything alone**. One sits on this
    host (`/etc/euler/share.json`, readable by every uid there and written only by the
    operator); the other is minted per recipient, **sealed to that recipient's X25519 public
    key** — read from the roster — and sent through the message spool, which they take
    with `msg act`: that runs `key-reconstruct`, unwraps their half, puts the two together,
    and writes their enc-key file.

    So a delivery has three independent parts and an attacker needs all of them: the message,
    the private key that opens it, and access to the host. That is the difference from an
    issued key, which is inert without the private key and nothing more — a stolen `~/.euler`
    plus a copy of the spool is enough for one and not for the other.

    The first run is the host's: with no local half yet (or one that predates the current
    master key) this **writes it and stops**, so nobody is sent a half they could not
    complete. Run it again to send. Off this host there is no shared half at all — use
    `host-authorize`.

    Args:
        identity: [asked] Who to send the other half to. Not asked — and not used — on the
            run that writes the repository's share.
        public_key: The recipient's 64-hex public key, for somebody the roster has no key for
            yet — a first grant, before anyone has been authorised. Defaults to '', which
            reads it from the roster.
    """
    from solver.web.msg.notify import notify_user
    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    existing: dict[str, str] | None = read_local_share()
    # A share that will not verify under the current key is one from before a rotation: any
    # half minted against it now would reconstruct into a key that no longer opens anything,
    # and the holder would find that out at the far end. Replace it and stop, as on a first run.
    if existing is None or not verify_master_key(existing, master_key):
        stale = 'The local share predates the current master key' if existing else 'No local share yet'
        try:
            _write_local_share(master_key)
        except PermissionError:
            console.print(f'[error]error:[/error] could not write [accent]{_share_label()}[/accent] '
                          '— run this from a terminal that can sudo (it is the operator\'s file).')
            return 1
        console.print(f'[success]{stale} — written [accent]{_share_label()}[/accent].[/success]\n'
                      '[muted]It stays on this host and is never committed. Now run '
                      '`key-split <identity>` to send the other half.[/muted]')
        return 0
    if not identity:
        raise Abort('key-split needs somebody to send the other half to', rc=ExitCodes.EXIT_USAGE)
    # The recipient's key first: everything after this mints or sends key material, and being
    # unable to address it is the one failure that should cost nothing.
    recipient: X25519PublicKey | None = _recipient_key(identity, public_key)
    if recipient is None:
        return 1
    try:
        share: str = _counterpart(master_key, existing['share'])
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    console.print(f'[primary]sending half the master key to:[/primary] {identity}\n'
                  f'[primary]wrapped to public key:[/primary] {public_key_hex(recipient)}')
    if not sure('Anyone holding the private key for that public key AND able to read this '
                'host can then decrypt every private solution. Send it?', phrase='send'):
        raise Abort('not sent')
    if not notify_user(identity, f'{KEY_SHARE_SUBJECT}{identity}',
                       _share_body(_wrap_share(recipient, share))):
        console.print('[error]error:[/error] could not deliver the share — nothing was sent. '
                      'Check the message spool and retry.')
        return 1
    console.print(f'[success]Sent to [accent]{identity}[/accent].[/success] '
                  '[muted]They run `msg act <id>` to put the halves together.[/muted]')
    _record_issue(identity, public_key_hex(recipient))
    return 0


def _record_issue(identity: str, public_key: str) -> None:
    """Record in the roster that this key was issued the master key, and say what to commit.

    An **act**, dated: what the operator did, at the moment it did it. Not a claim that they
    still hold the key — that fact lives in their own enc-key file — which is why the field is
    `key_issued` and not "has access". A rotation reads the key beside it; the date is for the
    person reading `users list`.

    The roster lives on the host and is writable by `euler-maint`, so a maintainer's grant
    records itself where the next rotation will read it — which it could not do while the file
    was tracked, since a web shell writes only its own clone. Best-effort all the same: the
    half is already sent by the time this runs, so a write that fails is reported rather than
    turned into a failed grant.
    """
    try:
        roster.upsert(identity, public_key=public_key, key_issued=roster.stamp())
    except OSError as exc:
        console.print(f'[warning]note:[/warning] the share is sent, but '
                      f'[accent]{roster.roster_path()}[/accent] could not be written ({exc}) — '
                      'without their key recorded, the next rotation cannot re-issue to them.')


@register(requires='reader')
def key_reconstruct(share: Annotated[str, Ask('The share you were sent')] = '') -> int:
    """Unwrap the half you were sent, complete it from the repository, store the key.

    What `msg act` does with a `key-split` message, and what to run by hand when the share
    reached you some other way. The half sent to you is **sealed to your public key**, so
    only this machine's private key opens it; the other half is the one this machine already
    holds (`/etc/euler/share.json` on the host). The reconstructed key is proved before
    anything is written, and then stored wrapped to your public key. Needs a private key
    already in place: run `user` first.

    Args:
        share: [asked] The share from your message — the wrapped blob as sent, or a bare
            262-hex share handed to you out of band. Asked for when it is not given.
    """
    if not share:
        raise Abort('key-reconstruct needs the share you were sent', rc=ExitCodes.EXIT_USAGE)
    share = share.strip().lower()
    if not _SHARE_RE.fullmatch(share):
        console.print('[error]error:[/error] that is not a share — expected the hex blob from '
                      'your message (or a bare 262-character share)')
        return 1
    local_share: dict[str, str] | None = read_local_share()
    if local_share is None:
        console.print('[error]error:[/error] this machine holds no half of the master key '
                      f'([accent]{_share_label()}[/accent]). On the host, ask a maintainer to '
                      'run `key-split`; off it, ask for `host-authorize` instead.')
        return 1
    try:
        private_key: X25519PrivateKey = load_private_key()
    except (FileNotFoundError, ValueError) as exc:
        console.print(f'[error]error:[/error] need a private key first ({exc}); run `user`')
        return 1
    # The private key does two jobs here, and this is the first: opening the half that was
    # wrapped to it. A blob meant for somebody else fails here, before any arithmetic.
    unwrapped: str | None = _unwrap_share(private_key, share)
    if unwrapped is None:
        return 1
    share = unwrapped
    try:
        master_key: bytes = _reconstruct_secret([local_share['share'], share])
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    # Prove it before writing. The file this replaces may be the only thing between this
    # machine and the whole private tree, and a wrong half is the ordinary failure here: an
    # old share, one meant for somebody else, or a machine whose half is from before a
    # rotation. Two independent checks, whichever is available — the share file's own
    # `verify`, and the enc-key file's when there is one.
    for source in (local_share, read_enc_key_file() if app_config.enc_key_file.exists() else {}):
        if wire.ENC_KEY_VERIFY in source and not verify_master_key(source, master_key):
            console.print('[error]error:[/error] the two halves do not make the master key '
                          '(wrong share, or this machine\'s half is stale) — nothing written')
            return 1
    # Last moment at which the key that opens HEAD is still the key in place — see
    # `save_issued_key`, which takes the same reading for the same reason.
    from solver.core.git import enc_key_arrived, private_local_edits
    local_edits = private_local_edits()
    write_enc_key_file(enc_key_payload(private_key.public_key(), master_key))
    console.print('[success]Master key reconstructed and stored[/success] '
                  f'[muted]({app_config.enc_key_file})[/muted]')
    enc_key_arrived(local_edits)
    return 0
