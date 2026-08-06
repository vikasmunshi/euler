#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Identity resolution → a :class:`~solver.auth.subject.Subject`.

Resolves *who* this process runs as and *what* it may do, **once** at startup,
across the identity planes (docs/web-server-guide.md § Identity). There is no
anonymous fallback; a process that matches no plane exits.

1. **Web shell** — `SOLVER_TICKET` in the environment: a **one-time shell
   ticket** minted by the auth service against the user's live session and
   redeemed here over the auth socket. Redemption consumes it and returns the
   authoritative `(email, profile)`; a missing/expired/reused ticket aborts, and
   so does one whose e-mail's :func:`system_slug` differs from the forking
   instance's `EULER_USER_SLUG` pin (that instance *is* the user's own uid, so a
   ticket for another user means misrouting or a bypass). Nothing env-carried is
   the credential — a ticket is the only thing that survives replay from a sibling
   process's `/proc/<pid>/environ`. In the per-user model the web channel is
   **not capped**: an `admin` account is web-reachable, its authority contained
   by its own uid + SRP, not by the channel.
2. **Instance identity** — a per-user service uid (the collaborator's
   :func:`system_slug`, e.g. `ue0f4a1`) whose ticketed shell has already redeemed
   and scrubbed the one-time ticket: the descendant `solver` processes it spawns
   (claude-solve's headless Claude, a nested `solver "…"`) carry no ticket and
   resolve from the instance itself. The uid *is* the collaborator; the handed-down
   `EULER_USER_EMAIL` is trusted only when :func:`system_slug` maps it back to the
   uid's own `EULER_USER_SLUG` pin, and the profile still comes from policy — so a
   child cannot forge either a different identity or a higher rung. Any *other*
   `euler-*` service uid, and any other member of the `euler-user` group, still
   aborts.
3. **Local terminal** — the OS login's profile from the `users` map;
   the **checkout owner floors to `admin`** when unlisted (you cannot
   lock yourself out), an explicit entry wins, and a real non-owner login without
   an entry is `contributor`. A service uid — an infra `euler-*` account or a
   member of the root-owned `euler-user` group — that is neither a ticketed web
   shell nor a properly-pinned per-user instance **aborts**, so a `reader` web
   shell cannot `unset SOLVER_TICKET` and re-exec `solver` to escalate: its uid
   pins the identity, and the profile follows from policy.

Absorbs the former `solver.utils.identity`. Stdlib-only and free of any
`solver.config` dependency (config imports this during construction); ticket
redemption lazily imports the equally-stdlib `solver.web.auth.client`.
"""
from __future__ import annotations

__all__ = ['resolve_subject', 'slugify', 'system_slug', 'per_user_login',
           'TICKET_ENV', 'INSTANCE_EMAIL_ENV']

import getpass
import grp
import hashlib
import os
import pwd
import re
from pathlib import Path

from solver.auth.authorizations import Authorizations
from solver.auth.subject import LADDER, Subject

#: Environment variable carrying the one-time shell ticket (set by the user service).
TICKET_ENV: str = 'SOLVER_TICKET'
#: The per-user instance's own system slug (`EULER_USER_SLUG=%i`), exported to the
#: PTY child: the redeemed ticket's e-mail must map to it (:func:`system_slug`), else the
#: shell aborts — the instance *is* that user's uid, so a mismatch is misrouting.
SLUG_PIN_ENV: str = 'EULER_USER_SLUG'
#: The bound e-mail of a per-user instance, handed *down* the process tree by a shell that
#: has already redeemed its ticket (:func:`resolve_subject` scrubs the one-time ticket and
#: exports this in its place). Descendant `solver` processes — claude-solve's headless
#: Claude, a nested `solver "…"` — resolve identity from it via the **instance-identity
#: plane**. Not a credential: it is trusted only when :func:`system_slug` maps it back to
#: the uid's own :data:`SLUG_PIN_ENV`, so a child cannot forge a different user past it.
INSTANCE_EMAIL_ENV: str = 'EULER_USER_EMAIL'
#: Infra service accounts are named `euler-*`; such a uid with no ticket must abort.
_SERVICE_PREFIX: str = 'euler-'
#: The root-owned parent group every per-user instance uid joins at provision time
#: (`scripts/setup/user.sh`). Since a per-user uid is named for the slug alone
#: (`ue0f4a1`) and no longer carries the `euler-` prefix, this membership — root
#: data, unwritable from a web shell — is what marks a login as a service uid that
#: must resolve through the instance-identity plane or abort.
_PER_USER_GROUP: str = 'euler-user'

_SLUG_KEEP = re.compile(r'[^a-z0-9._-]+')
#: Hex digits of the identity digest that *are* the system slug. The whole name is
#: `u` + this (`ue0f4a1`): a uid, a home directory, a socket name and a git branch,
#: so it is kept short and carries no e-mail local-part. 24 bits is ample separation for
#: a collaborator roster, and provisioning refuses to adopt a pre-existing account name,
#: so a hypothetical collision fails loudly rather than merging two people onto one uid.
_SYSTEM_SLUG_HEX: int = 6


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity* (per-user state dirs).

    Lower-cases, collapses any run of characters outside `[a-z0-9._-]` to a
    single `_`, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. `a@x`/`a_x`). Used
    for terminal identities; the web/system identity uses :func:`system_slug`.
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.')
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def system_slug(identity: str) -> str:
    """Return a **system-account** slug for *identity* — the per-user uid/home/socket name.

    Stricter and shorter than :func:`slugify`: `u` + a :data:`_SYSTEM_SLUG_HEX`-digit hash of
    the normalised identity (e.g. `ue0f4a1`), matching `^[a-z][a-z0-9]*$` so `useradd`'s
    `NAME_REGEX` accepts it bare — the uid *is* the slug, with no prefix and no home-grown
    length problem. The e-mail local-part is deliberately absent: this name shows up in
    `/home`, in the process table, and in a git branch, none of which need to publish who a
    collaborator is. The e-mail remains the login identity; this is only its derived system name.
    """
    digest = hashlib.sha1(identity.strip().lower().encode('utf-8')).hexdigest()
    return f'u{digest[:_SYSTEM_SLUG_HEX]}'


def per_user_login(os_login: str) -> bool:
    """True if *os_login* is a provisioned per-user instance uid (`euler-user` member).

    Root-owned group data — a web shell cannot add or remove itself — so this is the
    discriminator that replaces the old `euler-user-` name prefix: such a login must
    resolve through the instance-identity plane or abort. Both the supplementary
    membership and a primary-group match count; an absent group means none are
    provisioned here.
    """
    try:
        group = grp.getgrnam(_PER_USER_GROUP)
    except KeyError:
        return False
    if os_login in group.gr_mem:
        return True
    try:
        return pwd.getpwnam(os_login).pw_gid == group.gr_gid
    except KeyError:
        return False


def _redeem_ticket(ticket: str) -> tuple[str, str]:
    """Redeem the one-time shell ticket at the auth service; `(email, profile)`.

    Any failure — service down, ticket unknown/expired/already redeemed — raises
    :class:`SystemExit`: an unvouched web shell must not start.
    """
    from solver.config.env import load_spec
    from solver.web.auth.client import request
    socket_path = load_spec('auth').raw('socket_path')
    try:
        status, data = request(socket_path, 'POST', '/shell-ticket/redeem', body={'ticket': ticket})
    except OSError as exc:
        raise SystemExit(f'identity: auth service unreachable ({exc})') from None
    if status != 200 or not isinstance(data, dict):
        raise SystemExit('identity: shell ticket rejected')
    email, profile = str(data.get('email', '')), str(data.get('profile', ''))
    if not email or not profile:
        raise SystemExit('identity: malformed ticket redemption')
    return email, profile


def _owns_checkout(root_dir: Path) -> bool:
    """True if the current process uid owns the repo checkout (the local trust anchor)."""
    try:
        return os.getuid() == root_dir.stat().st_uid
    except OSError:
        return False


def _instance_identity(os_login: str, authz: Authorizations) -> Subject | None:
    """Resolve a per-user service uid to its bound collaborator, ticket-free.

    The **instance-identity plane**: a per-user uid is provisioned for exactly one
    collaborator, and its ticketed PTY shell scrubs the one-time ticket once
    redeemed. The descendant `solver` processes that shell spawns —
    claude-solve's headless Claude, a nested `solver "…"` — therefore have *no*
    ticket; they re-resolve here instead of aborting.

    Trust is the OS uid, cross-checked three ways: the account **is** the pin (the
    uid is named for the slug), the handed-down :data:`INSTANCE_EMAIL_ENV` maps back
    to that pin under :func:`system_slug`, and the pin is present. The e-mail is an
    env value a child could rewrite — but only a value whose `system_slug` equals
    this uid's own name survives, i.e. the instance's own user, so it cannot forge a
    different identity. The **profile** comes from the same policy the auth service
    reads (`authorizations.json`), never from the environment, so a child cannot
    forge a higher rung; an unlisted user floors to the weakest rung. Returns
    `None` when this is not a properly-pinned per-user instance (an infra
    `euler-*` account, or a group member whose env does not line up), so the
    caller still aborts.
    """
    email = os.environ.get(INSTANCE_EMAIL_ENV, '').strip()
    pin = os.environ.get(SLUG_PIN_ENV, '').strip()
    if not email or not pin or os_login != pin or system_slug(email) != pin:
        return None
    profile = authz.profile_for(email) or LADDER[0]  # unlisted → least privilege (fail closed low)
    return Subject(user=email, slug=pin, channel='web', auth_method='instance-identity', profile=profile)


def resolve_subject(root_dir: Path, authz: Authorizations | None = None) -> Subject:
    """Resolve the current :class:`Subject` (identity + profile).

    *authz* is the loaded policy; if omitted it is loaded (deployed SoR → built-in
    default). Raises :class:`SystemExit` when no identity plane matches.
    """
    if authz is None:
        authz = Authorizations.load()

    ticket = os.environ.get(TICKET_ENV, '').strip()
    if ticket:
        email, profile = _redeem_ticket(ticket)     # authoritative (email, profile); admin uncapped
        slug = system_slug(email)
        pin = os.environ.get(SLUG_PIN_ENV, '').strip()
        if pin and slug != pin:
            # The forking instance *is* this user's uid (named <pin>):
            # a ticket for another user means misrouting or a bypass attempt, and this
            # process — with that uid's home, keys, and clone — must not run as them.
            raise SystemExit(f'identity: ticket user {slug!r} does not match '
                             f'this instance ({pin!r}) — refusing to start')
        return Subject(user=email, slug=slug, channel='web',
                       auth_method='shell-ticket', profile=profile)

    try:
        os_login = getpass.getuser()
    except OSError:
        raise SystemExit('identity: could not determine the OS login') from None
    if os_login.startswith(_SERVICE_PREFIX) or per_user_login(os_login):
        subject = _instance_identity(os_login, authz)
        if subject is not None:
            return subject
        raise SystemExit(f'identity: service account {os_login!r} has no shell ticket — refusing to start')

    is_owner = _owns_checkout(root_dir)
    mapped = authz.profile_for(os_login)             # unlisted → owner floors to admin, else contributor
    profile = mapped if mapped is not None else ('admin' if is_owner else 'contributor')
    return Subject(user=os_login, slug=slugify(os_login), channel='terminal',
                   auth_method='checkout-owner' if is_owner else 'os-login', profile=profile)
