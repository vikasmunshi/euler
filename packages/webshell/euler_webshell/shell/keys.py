#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Key distribution: issuing the master key over the message spool and by mail.

docs/package-guide.md § 6. The solver shell holds and receives keys (:mod:`solver.crypto.keys`);
*sending* them needs the roster (`/etc/euler/roster/users.json`, :mod:`euler_webshell.roster`), the
spool and the mail relay, which only the web host has. So these commands load with the web
shell's extension, not the solver shell's manifest:

Granting the key to somebody is one act with two halves. `user-authorize` records their
**public key** in the roster and delivers half the master key, sealed to that key; the other
half is the host's share file, which every uid there can read and only the operator writes.
`key-reconstruct` puts the two together at their end. So no single artefact is ever the key —
the message, the private key that opens it, and access to the host all count — and `key-split`
is the same delivery without the request-thread handling, plus the run that lays the local half
down in the first place.

**Off the host** there is no shared half to complete, so the pair is `host-authorize` (seal the
whole master key to a public key and mail it) and `host-unlock` (take the mailed block and
install it).

`key-rekey`'s re-issue is here too, as the body that replaces the solver's (`overlays.toml`).

Shell commands registered here: `user-authorize`, `key-split`, `host-authorize`.
"""
from __future__ import annotations

__all__ = ['host_authorize', 'key_rekey', 'key_split', 'user_authorize']

import os
import re
from json import dumps
from typing import Annotated, Any

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey

from euler_webshell import roster
from solver.config import ExitCodes, config as app_config
from solver.core.notices import KEY_ISSUE_SUBJECT, KEY_REQUEST_SUBJECT, KEY_SHARE_SUBJECT
from solver.crypto.ciphers import (enc_key_payload, load_private_key, public_key_hex, read_master_key,
                                   verify_master_key)
from solver.crypto.keys import (PUBLIC_KEY_RE, counterpart, public_key_from, read_local_share,
                                rotate_master_key, sealed_block, share_label, wrap_share,
                                write_local_share)
from solver.shell import console, register
from solver.shell.dialogue import Abort, Ask, sure
from euler_webshell.users import registered_public_keys
from euler_site.auth.mail import Mailer
from euler_webshell.msg.notify import dismiss_thread, notify_user, read_thread


#: A spool thread id (`secrets.token_hex(8)`) — half a public key's length, which is what
#: lets `user-authorize` take either without a flag to say which it was given.
_THREAD_ID_RE = re.compile(r'[0-9a-f]{16}')


#: The loopback mail relay, as `auth.env` sets it for the service — repeated here because the
#: operator's terminal cannot read that file (`root:euler-auth 0640`) and needs no secret to
#: submit: the relay holds the credentials, and the firewall decides who may reach it.
_SMTP_RELAY: str = os.environ.get('EULER_SMTP_RELAY', '127.0.0.1:8025')


def key_rekey() -> int:
    """`key-rekey`, re-issuing: rotate, then send the new key to every registered public key.

    Replaces the solver shell's body (`overlays.toml`). The list of who "everyone else" is comes
    from the **roster** — each holder's `public_key` in `/etc/euler/roster/users.json`, written
    by the grant that issued to them. It holds only *public* keys, which is why losing it costs
    nothing but a round of re-authorization.

    Each holder is sent their own payload through the message spool, exactly as
    `user-authorize` does; they run `msg act` on it to take it. An account with no registered
    public key cannot be re-issued to and is named, not skipped silently — that person loses
    access at this rotation, which is sometimes the intent and must never be a surprise.
    """
    try:
        read_master_key()  # proof of authority: must currently hold and verify the master key
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] refusing to rekey -- current key check failed ({exc})')
        return 1
    holders = registered_public_keys()
    if holders is None:
        console.print('[error]error:[/error] could not read the roster — rekey needs it to know who '
                      f'to re-issue to (is [accent]{share_label()}[/accent] present and readable?)')
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
    rc, new_master = rotate_master_key()
    if rc != 0:
        return rc
    for identity, public_key in named.items():
        if public_key == mine:
            continue
        pub = X25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
        sent = notify_user(identity, f'{KEY_ISSUE_SUBJECT}rotated master key',
                           _issue_body(enc_key_payload(pub, new_master)))
        console.print(f'  {"sent to" if sent else "COULD NOT REACH"} [accent]{identity}[/accent]')
    console.print('[success]Rotated, published, and issued.[/success]')
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
    thread: dict[str, Any] | None = read_thread(thread_id)
    if thread is None:
        console.print(f'[error]error:[/error] cannot read message [accent]{thread_id}[/accent] '
                      '(no such thread, not yours to read, or the spool is unreachable)')
        return None
    if not str(thread.get('subject', '')).startswith(KEY_REQUEST_SUBJECT):
        console.print(f'[error]error:[/error] message [accent]{thread_id}[/accent] is not a key '
                      'authorization request — authorise the public key directly instead')
        return None
    found = PUBLIC_KEY_RE.findall(str(thread.get('body', '')))
    if len(found) != 1:
        console.print(f'[error]error:[/error] found [accent]{len(found)}[/accent] public keys in '
                      f'message {thread_id}; expected exactly one — pass the key itself')
        return None
    identity = str(thread.get('author_name') or thread.get('author') or '')
    return found[0], identity


def _needs_an_identity(bound: dict[str, Any]) -> bool:
    """Whether the target carries no identity of its own, and so has to be told one.

    A message id names its author, and taking the identity from the thread is the whole
    point of the request form. Only a bare public key — which arrived some other way — needs
    asking, and asking anyway would offer to override what the request already said.
    """
    return not _THREAD_ID_RE.fullmatch(str(bound.get('target') or '').strip().lower())


@register(requires='maintainer', aliases=('authorize',))
def user_authorize(target: Annotated[str, Ask('Which key request?', choices='key_requests',
                                              strict=False,
                                              empty='no key requests waiting')],
                   identity: Annotated[str, Ask('Who does the key belong to?',
                                                choices='accounts', strict=False,
                                                when=_needs_an_identity)] = '') -> int:
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
        target: [asked] The 16-hex id of a key-authorization message, or a 64-hex public
            key. Offered as a menu of the waiting requests when omitted; not strict, so a
            bare key can still be pasted.
        identity: [asked] Who the key belongs to. Taken from the thread for the message
            form, so it is only asked for the bare-key form — where there is nobody to send
            it to otherwise.
    """
    token = target.strip().lower()
    thread_id = ''
    if _THREAD_ID_RE.fullmatch(token):
        resolved = _resolve_key_request(token)
        if resolved is None:
            return 1
        thread_id, public_key, identity = token, resolved[0], resolved[1]
    elif PUBLIC_KEY_RE.fullmatch(token):
        public_key = token
        if not identity:
            console.print('[error]error:[/error] a bare public key needs an identity — there is '
                          'nobody to send the key to otherwise')
            return 1
    else:
        console.print('[error]error:[/error] expected a 64-character public key or a '
                      '16-character message id')
        return 1
    if public_key_from(public_key) is None:
        return 1

    # The repository's half has to be current *before* anything is sent, and this is the one
    # place that cannot be discovered at the far end: `key-split` would lay a fresh half and
    # report success without sending, and the request would then be dismissed as worked.
    if not _local_share_ready():
        console.print('[error]error:[/error] the repository has no current half of the master '
                      f'key ([accent]{share_label()}[/accent]). Run [accent]key-split[/accent] '
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
    recipient: X25519PublicKey | None = public_key_from(public_key.strip().lower())
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
    block: str = sealed_block(enc_key_payload(recipient, master_key))
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


def _issue_body(payload: dict[str, str]) -> str:
    """The message body carrying an enc-key payload — a line of prose, then the JSON.

    `msg act` reads the JSON object out of it, so the prose above is free to change and the
    braces are the contract. Kept human-readable on purpose: the recipient sees what arrived
    and what to do with it, not an opaque blob.
    """
    return ('Your master-key access. Run `msg act <id of this message>` to write it to '
            'your enc-key file; the private solutions decrypt in place once you do.\n\n'
            + dumps(payload, indent=2) + '\n')


def _share_body(share: str) -> str:
    """The message body carrying one half of the master key, wrapped to its recipient.

    `msg act` reads the blob out of it (:func:`share_in_message`), so the prose is free to
    change and the run of hex is the contract — exactly as the braces are for an issued key.
    There must be **one** such token in it and no other.
    """
    return ('Half of the master key, sealed to your public key. The other half is already on '
            f'this host ({share_label()}) — run `msg act <id of this message>` to unwrap this '
            'one, put the two together, and write your enc-key file. The private solutions '
            'decrypt in place once you do.\n\n'
            f'share: {share}\n')


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
    return public_key_from(token)


def _holds_a_key(account: Any) -> bool:
    """Whether a share can actually be sealed to *account* — the filter a share menu needs.

    An account with no public key is left out rather than offered: `key-split` would refuse
    it a moment later, and a menu must never offer what the command will then refuse. A
    filter on `{accounts}` rather than a variable of its own, because "who has a key" is a
    property of an account, not a second list of people.
    """
    return bool(getattr(account, 'holds_key', False))


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


@register(requires='maintainer')
def key_split(identity: Annotated[str, Ask('Who should receive the other half?',
                                           choices='accounts', which=_holds_a_key,
                                           when=_sends_a_share,
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
            write_local_share(master_key)
        except PermissionError:
            console.print(f'[error]error:[/error] could not write [accent]{share_label()}[/accent] '
                          '— run this from a terminal that can sudo (it is the operator\'s file).')
            return 1
        console.print(f'[success]{stale} — written [accent]{share_label()}[/accent].[/success]\n'
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
        share: str = counterpart(master_key, existing['share'])
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    console.print(f'[primary]sending half the master key to:[/primary] {identity}\n'
                  f'[primary]wrapped to public key:[/primary] {public_key_hex(recipient)}')
    if not sure('Anyone holding the private key for that public key AND able to read this '
                'host can then decrypt every private solution. Send it?', phrase='send'):
        raise Abort('not sent')
    if not notify_user(identity, f'{KEY_SHARE_SUBJECT}{identity}',
                       _share_body(wrap_share(recipient, share))):
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
