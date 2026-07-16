#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Outbound mail via the loopback relay.

The auth service holds **no** SMTP credentials: it submits over plain loopback
SMTP to the ``euler-smtp`` relay (``EULER_SMTP_RELAY``), which is the sole
holder of the Gmail app password and the sole uid the egress firewall permits
on ``:587``. The relay forces the envelope sender, so this client only authors
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

    def send_otp(self, rcpt: str, otp: str) -> None:
        """Email the one-time code proving live mailbox control."""
        self._send(rcpt, 'Your euler verification code',
                   f'Your verification code is:\n\n    {otp}\n\n'
                   'It is valid for 10 minutes and allows 5 attempts.\n')
