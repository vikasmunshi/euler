#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Send the registration / reset link by email via Gmail SMTP.

Credentials come from the project ``.env`` (the same file holding
``ANTHROPIC_API_KEY`` / the name.com token), read with python-dotenv and
overridable by the process environment:

    SMTP_ADDRESS=you@gmail.com
    SMTP_APP_PASSWORD=<Gmail App Password>

The App Password is a 16-character Google app-specific password (2-Step
Verification must be enabled on the account). Sending is synchronous; callers on
the event loop should run it in an executor.
"""
from __future__ import annotations

__all__ = ['smtp_configured', 'registration_link', 'send_registration_link']

import os
import smtplib
from email.message import EmailMessage

from solver.config import config
from solver.web.auth import policy

_SMTP_HOST = 'smtp.gmail.com'
_SMTP_PORT = 587
_DEFAULT_BASE_URL = 'https://euler.vikasmunshi.com'


def _env() -> dict[str, str | None]:
    """Merged config: the project `.env` (if python-dotenv is available) overlaid by os.environ."""
    values: dict[str, str | None] = {}
    try:
        from dotenv import dotenv_values
        values.update(dotenv_values(config.root_dir / '.env'))
    except ImportError:
        pass
    values.update(os.environ)
    return values


def _credentials() -> tuple[str, str] | None:
    """Return (address, app_password) from .env / environment, or None if unset."""
    values = _env()
    address = values.get('SMTP_ADDRESS')
    password = values.get('SMTP_APP_PASSWORD')
    return (address, password) if address and password else None


def _base_url() -> str:
    """Public site base URL for links in emails (EULER_BASE_URL in .env; sensible default)."""
    return (_env().get('EULER_BASE_URL') or _DEFAULT_BASE_URL).rstrip('/')


def registration_link(token: str) -> str:
    """The set-password URL carrying `token` (the register page reads `?token=`)."""
    return f'{_base_url()}/register?token={token}'


def smtp_configured() -> bool:
    """True if Gmail SMTP credentials are available."""
    return _credentials() is not None


def send_registration_link(to_email: str, token: str, kind: str = 'register') -> None:
    """Email the secure `token` link to `to_email` via Gmail SMTP (STARTTLS).

    `kind` ('register' or 'reset') only tailors the wording. Raises RuntimeError if
    credentials are missing, or an smtplib error on failure.
    """
    credentials = _credentials()
    if credentials is None:
        raise RuntimeError('SMTP not configured: set SMTP_ADDRESS and SMTP_APP_PASSWORD in .env')
    address, password = credentials

    link = registration_link(token)
    hours = policy.REGISTRATION_TTL_SECONDS // 3600
    if kind == 'reset':
        subject = 'Reset your solver password'
        intro = 'Use this secure link to choose a new password for your solver account:'
    else:
        subject = 'Complete your solver registration'
        intro = 'You have been invited to solver. Use this secure link to set your password:'

    message = EmailMessage()
    message['From'] = address
    message['To'] = to_email
    message['Subject'] = subject
    message.set_content(
        f'{intro}\n\n    {link}\n\n'
        f'The link expires in {hours} hours and can be used once. '
        f'If you did not request this, you can ignore this email.\n')

    with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(address, password)
        server.send_message(message)
