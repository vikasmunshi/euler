#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Outbound mail via the loopback relay.

The auth service holds **no** SMTP credentials: it submits over plain loopback
SMTP to the `euler-smtp` relay (`EULER_SMTP_RELAY`), which is the sole
holder of the Gmail app password and the sole uid the egress firewall permits
on `:587`. The relay forces the envelope sender, so this client only authors
headers and body.

Never log message bodies here — they carry invite links and OTPs.
"""
from __future__ import annotations

__all__ = ['Mailer']

import logging
import smtplib
from email.message import EmailMessage

log = logging.getLogger('euler-auth.mail')


class Mailer:
    """Compose and submit the auth flows' mail through the loopback relay."""

    def __init__(self, relay: str, base_url: str) -> None:
        host, _, port = relay.rpartition(':')
        self._host = host or '127.0.0.1'
        self._port = int(port or 8025)
        self._base_url = base_url
        # Header From — informational; the relay/Gmail rewrite the real sender.
        self._from = f'euler <no-reply@{base_url.split("//")[-1]}>'

    def _send(self, rcpt: str, subject: str, body: str) -> None:
        """Submit one message; raises on relay failure (caller decides the response)."""
        message = EmailMessage()
        message['From'] = self._from
        message['To'] = rcpt
        message['Subject'] = subject
        message.set_content(body)
        with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
            smtp.send_message(message)
        log.info('sent %r to %s', subject, rcpt)

    def send_invite(self, rcpt: str, token: str, kind: str) -> None:
        """Email the registration (or reset) link for a freshly minted invite."""
        page = 'register' if kind == 'register' else 'reset'
        url = f'{self._base_url}/{page}?token={token}'
        if kind == 'register':
            subject = 'Your euler account invitation'
            body = (f'You have been invited to the euler solver at {self._base_url}.\n\n'
                    f'Open this link to register (valid for 7 days):\n\n    {url}\n\n'
                    'If you were not expecting this invitation, ignore this mail.\n')
        else:
            subject = 'euler password reset'
            body = (f'A password reset was requested for this address at {self._base_url}.\n\n'
                    f'Open this link to continue (valid for 7 days):\n\n    {url}\n\n'
                    'If you did not request it, ignore this mail — nothing changes.\n')
        self._send(rcpt, subject, body)

    def send_invite_request(self, rcpt: str, name: str, email: str, remarks: str) -> None:
        """Nudge the operator that a prospective collaborator asked for an invite.

        The requester's name/email/remarks ride in the **body** only (never a header),
        and reach here already control-char-stripped, so there is no header-injection
        surface — *rcpt* is the trusted operator address from config.

        The mail reports the request and nothing else. It used to spell out the shell
        commands to act on it and they rotted — naming two verbs that no longer exist —
        because a mail body is the one copy of the interface that no rename touches and
        no test reads. The queue itself is the instruction: it is on the operator's
        `users` roster, which does carry the live verbs.
        """
        self._send(rcpt, 'euler account request',
                   f'Someone requested an account at {self._base_url}.\n\n'
                   f'Name:    {name or "(none)"}\n'
                   f'Email:   {email}\n'
                   f'Remarks: {remarks or "(none)"}\n\n'
                   'The request is queued for review in the solver shell.\n')

    def send_master_key(self, rcpt: str, block: str) -> None:
        """Email a master key sealed to one public key — the off-host grant (`host-authorize`).

        The one mail body that carries key material, and it may: the payload is wrapped to a
        public key, so it is inert to the mail provider, the operator's own mailbox, and
        anyone who later reads either. What makes it usable at the far end is that the block
        is **delimited and quoted verbatim** — the recipient copies between the markers into
        `host-unlock`, and no mail client's line wrapping can be mistaken for content.

        Unlike every other mail here this one is submitted from the *operator's terminal*, not
        the auth service: the egress firewall bars the per-user uids from the relay, and this
        is an admin act by construction.
        """
        self._send(rcpt, 'euler master key (sealed)',
                   'Below is the euler master key, sealed to the public key you supplied. It is '
                   'useless to anyone without the matching private key.\n\n'
                   'On the machine that holds that private key, run:\n\n'
                   '    solver "host-unlock"\n\n'
                   'and paste everything between the markers when it asks.\n\n'
                   f'{block}\n'
                   'If you did not ask for this, tell the sender — and ignore it.\n')

    def send_otp(self, rcpt: str, otp: str) -> None:
        """Email the one-time code proving live mailbox control."""
        self._send(rcpt, 'Your euler verification code',
                   f'Your verification code is:\n\n    {otp}\n\n'
                   'It is valid for 10 minutes and allows 5 attempts.\n')
