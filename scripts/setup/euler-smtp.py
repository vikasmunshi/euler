#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""euler-smtp — loopback SMTP submission relay (DD-8, docs/secure-web-server.md).

A minimal, stdlib-only ESMTP listener on loopback that relays every accepted
message upstream (Gmail submission, STARTTLS + app password). It exists so that
the app tier needs **no** direct-internet exception and **no** mail credentials:

  - It is the sole holder of the Gmail credentials (/etc/euler/smtp.env,
    root:euler-smtp 0640) and — via the nftables egress ruleset
    (scripts/setup/firewall.sh) — the sole euler-* uid permitted tcp :587.
  - euler-auth submits OTP/invite mail over plain loopback SMTP with no
    credentials of its own (EULER_SMTP_RELAY=127.0.0.1:8025).
  - The envelope sender is always forced to SMTP_ADDRESS; clients cannot
    choose an origin identity.

Deliberately *not* a general MTA: no queue (a failed upstream send returns a
transient 451 and the client retries), no TLS/auth on the loopback listener
(loopback + the firewall's relay guard are the access control), tight size and
recipient limits. Message bodies are never logged (they carry OTPs).

Deployed to /usr/local/bin/euler-smtp by scripts/setup/smtp.sh and run by the
root-owned euler-smtp.service as the dedicated `euler-smtp` user. Runs on the
system python3 (stdlib only).

Configuration (environment, from /etc/euler/smtp.env):
  EULER_SMTP_LISTEN   listen address, default 127.0.0.1:8025
  SMTP_HOST           upstream submission host, default smtp.gmail.com
  SMTP_PORT           upstream submission port, default 587
  SMTP_ADDRESS        Gmail address: upstream login user *and* forced sender
  SMTP_APP_PASSWORD   Gmail app password (upstream login)

Author: Vikas Munshi <vikas.munshi@gmail.com>
Licensed under the MIT License.
"""
from __future__ import annotations

import asyncio
import logging
import os
import smtplib
import sys

MAX_LINE = 4096            # RFC 5321 command lines are far shorter
MAX_SIZE = 64 * 1024       # OTP/invite mail is tiny; cap DATA hard
MAX_RCPT = 5
SESSION_TIMEOUT = 60.0     # seconds of inactivity before the connection is dropped

log = logging.getLogger('euler-smtp')


def _require_env(name: str) -> str:
    value = os.environ.get(name, '').strip()
    if not value:
        log.error('missing required environment variable %s', name)
        sys.exit(2)
    return value


def _relay(sender: str, rcpts: list[str], data: bytes,
           host: str, port: int, password: str) -> None:
    """Submit one message upstream (blocking; run in a thread). Raises on failure."""
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.sendmail(sender, rcpts, data)


class Session:
    """One loopback SMTP session: minimal ESMTP state machine."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 config: dict[str, object]) -> None:
        self.reader = reader
        self.writer = writer
        self.config = config
        self.mail_from: str | None = None
        self.rcpts: list[str] = []

    async def send(self, line: str) -> None:
        self.writer.write((line + '\r\n').encode('ascii'))
        await self.writer.drain()

    async def recv_line(self) -> bytes:
        """Read one CRLF-terminated line, bounded by MAX_LINE and the idle timeout."""
        line = await asyncio.wait_for(self.reader.readline(), SESSION_TIMEOUT)
        if len(line) > MAX_LINE:
            raise ValueError('line too long')
        return line

    def reset(self) -> None:
        self.mail_from = None
        self.rcpts = []

    async def run(self) -> None:
        await self.send('220 euler-smtp loopback relay ready')
        while True:
            raw = await self.recv_line()
            if not raw:                      # EOF — client went away
                return
            line = raw.decode('ascii', 'replace').rstrip('\r\n')
            verb, _, arg = line.partition(' ')
            verb = verb.upper()
            if verb in ('EHLO', 'HELO'):
                await self.send(f'250-euler-smtp\r\n250 SIZE {MAX_SIZE}')
            elif verb == 'MAIL':             # MAIL FROM:<...> — sender is *ignored* (forced)
                self.reset()
                self.mail_from = arg
                await self.send('250 OK (sender is forced to the relay account)')
            elif verb == 'RCPT':
                if self.mail_from is None:
                    await self.send('503 need MAIL first')
                elif len(self.rcpts) >= MAX_RCPT:
                    await self.send('452 too many recipients')
                else:
                    addr = arg.partition(':')[2].strip().strip('<>')
                    if '@' not in addr:
                        await self.send('501 bad recipient')
                    else:
                        self.rcpts.append(addr)
                        await self.send('250 OK')
            elif verb == 'DATA':
                if not self.rcpts:
                    await self.send('503 need RCPT first')
                else:
                    await self.handle_data()
            elif verb == 'RSET':
                self.reset()
                await self.send('250 OK')
            elif verb == 'NOOP':
                await self.send('250 OK')
            elif verb == 'QUIT':
                await self.send('221 bye')
                return
            else:
                await self.send('502 command not implemented')

    async def handle_data(self) -> None:
        await self.send('354 end with <CRLF>.<CRLF>')
        chunks: list[bytes] = []
        size = 0
        while True:
            raw = await self.recv_line()
            if not raw:
                return                       # EOF mid-DATA: drop silently
            if raw.rstrip(b'\r\n') == b'.':
                break
            if raw.startswith(b'.'):         # dot-unstuffing (RFC 5321 §4.5.2)
                raw = raw[1:]
            size += len(raw)
            if size > MAX_SIZE:
                await self.send('552 message too large')
                self.reset()
                return
            chunks.append(raw)
        data = b''.join(chunks)
        sender = str(self.config['address'])
        rcpts = list(self.rcpts)
        self.reset()
        try:
            await asyncio.to_thread(_relay, sender, rcpts, data,
                                    str(self.config['host']), int(self.config['port']),  # type: ignore[arg-type]
                                    str(self.config['password']))
        except Exception as exc:             # transient to the client; never log the body
            log.warning('relay failed: %d rcpt, %d bytes: %s', len(rcpts), len(data), exc)
            await self.send('451 upstream submission failed, try again later')
            return
        log.info('relayed: %d rcpt, %d bytes', len(rcpts), len(data))
        await self.send('250 OK message relayed')


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 config: dict[str, object]) -> None:
    try:
        await Session(reader, writer, config).run()
    except (asyncio.TimeoutError, ValueError, ConnectionError):
        pass                                 # idle/oversized/vanished client — just drop it
    except Exception:
        log.exception('session error')
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    listen = os.environ.get('EULER_SMTP_LISTEN', '127.0.0.1:8025')
    bind_host, _, bind_port = listen.rpartition(':')
    config: dict[str, object] = {
        'host': os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
        'port': int(os.environ.get('SMTP_PORT', '587')),
        'address': _require_env('SMTP_ADDRESS'),
        'password': _require_env('SMTP_APP_PASSWORD'),
    }
    server = await asyncio.start_server(
        lambda r, w: handle(r, w, config), bind_host, int(bind_port), limit=MAX_LINE)
    log.info('listening on %s, upstream %s:%s as %s',
             listen, config['host'], config['port'], config['address'])
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
