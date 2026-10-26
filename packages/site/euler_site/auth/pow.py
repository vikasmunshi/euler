#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Proof of work for the unauthenticated forms that make the service send mail.

`/forgot` and `/request-invite` each cost the operator something per request — a mail, a queue
entry — and anyone can post them. The mail budgets (`policy.MAIL_*`) cap the damage; this makes
each request cost the *sender* something first, so a script cannot spend those budgets for free.

The scheme is hashcash. The page carries a **stamp** the server minted and signed —
`<issued>.<random>.<hmac>` — and the browser (`assets/pow.js`) searches for a nonce such that
`SHA-256("<stamp>:<nonce>")` begins with :data:`~euler_site.auth.policy.POW_BITS` zero bits,
then submits both. The server checks the signature (so a stamp cannot be invented), its age (so
one cannot be stockpiled), the work, and that it has not been spent (so one solve buys one
request). Nothing is stored per stamp until it is spent, and spent stamps are forgotten when
they would have expired anyway.

A person waits about a second; the cost scales with the request count, which is the point.
"""
from __future__ import annotations

__all__ = ['ProofOfWork', 'leading_zero_bits']

import hmac
import secrets
import time
from hashlib import sha256


def leading_zero_bits(digest: bytes) -> int:
    """How many zero bits *digest* starts with."""
    bits = 0
    for byte in digest:
        if byte:
            return bits + 8 - byte.bit_length()
        bits += 8
    return bits


class ProofOfWork:
    """Mints stamps and checks solved ones, each stamp good for one request."""

    def __init__(self, secret: bytes, bits: int, ttl_seconds: int) -> None:
        self._secret = secret
        self.bits = bits
        self._ttl = ttl_seconds
        #: Spent stamps → when they expire; dropped once past it (the age check covers them).
        self._spent: dict[str, float] = {}

    def _sign(self, body: str) -> str:
        return hmac.new(self._secret, body.encode(), sha256).hexdigest()[:32]

    def stamp(self) -> str:
        """A fresh stamp for a form to carry."""
        body = f'{int(time.time())}.{secrets.token_hex(8)}'
        return f'{body}.{self._sign(body)}'

    def check(self, stamp: str, nonce: str) -> bool:
        """Whether *nonce* is a valid, unspent solution of *stamp* — spending it if so."""
        now = time.time()
        self._spent = {key: expiry for key, expiry in self._spent.items() if expiry > now}
        issued, _, rest = stamp.partition('.')
        _random, _, signature = rest.partition('.')
        if not (issued.isdigit() and signature and len(nonce) <= 32):
            return False
        if not hmac.compare_digest(signature, self._sign(stamp.rsplit('.', 1)[0])):
            return False
        if not 0 <= now - int(issued) <= self._ttl or stamp in self._spent:
            return False
        if leading_zero_bits(sha256(f'{stamp}:{nonce}'.encode()).digest()) < self.bits:
            return False
        self._spent[stamp] = int(issued) + self._ttl
        return True
