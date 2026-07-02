#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Secure Remote Password (SRP-6a) primitives for web authentication.

SRP lets the server authenticate a user's password **without ever storing or
receiving the password itself**. At registration the client turns its
`(email, password)` into a *verifier* `v = g**x mod N` (where the private
exponent `x` is derived from a random salt and the password) and the server
keeps only the salt and `v`. Recovering the password from `v` is a discrete-log
problem, so the stored material is safe at rest.

Authentication is a zero-knowledge handshake (RFC 5054 / SRP-6a):

    client                                              server
    a, A = g**a                ──A──▶
                               ◀─salt, B──             b, B = k*v + g**b
    u = H(A,B)                                         u = H(A,B)
    S = (B - k*g**x)**(a+u*x)                          S = (A * v**u)**b
    K = H(S)                                           K = H(S)
    M1 = H(...,K)              ──M1──▶                 verify M1, derive M2
                               ◀──M2──                 M2 = H(A, M1, K)
    verify M2

Both endpoints arrive at the same shared key `K` only when the password used by
the client matches the verifier held by the server; neither `a`, `b`, `x`, nor
the password ever crosses the wire. This module implements both ends
(:class:`SrpClient`, :class:`SrpServer`) plus :func:`verify_password`, which runs
the whole handshake locally — the path used when a password *is* available
server-side (e.g. the `users add --password` bootstrap) and must be checked
against a stored verifier.

This is **web-authentication** material only: it lives under ``solver.web`` and
shares no code or key material with ``solver.crypto`` (the git-filter solution
encryption). Logging in gates web access; it does not unlock the encryption
master key.

The group is the RFC 5054 2048-bit safe prime with generator ``g = 2`` and
SHA-256 throughout; :data:`VERSION` records this so the parameters can evolve
later. Integer values fed to the hash (``A``, ``B``, ``S``) are left-padded to
the byte length of ``N`` (``PAD``), which a browser-side client must match
byte-for-byte to interoperate.
"""
from __future__ import annotations

__all__ = ['SrpClient', 'SrpServer', 'SrpToken', 'make_srp_token', 'compute_verifier',
           'verify_password', 'VERSION']

import secrets
from hashlib import sha256
from typing import NamedTuple

# RFC 5054, Appendix A — 2048-bit group ("N") and generator ("g").
_N: int = int(
    'AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050'
    'A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50'
    'E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B8'
    '55F97993EC975EEAA80D740ADBF4FF747359D041D5C33EA71D281E446B14773B'
    'CA97B43A23FB801676BD207A436C6481F1D2B9078717461A5B9D32E688F87748'
    '544523B524B0D57D5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6'
    'AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6'
    '94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F9E4AFF73', 16)
_g: int = 2
_N_BYTES: int = (_N.bit_length() + 7) // 8

#: Version tag stamped into every token; encodes the hash + group so they can change later.
VERSION: str = 'srp6a-sha256-2048'
#: Random salt length in bytes used when minting a fresh verifier.
_SALT_BYTES: int = 16


def _hash(*parts: bytes) -> bytes:
    """Return the SHA-256 digest of the concatenated byte chunks."""
    digest = sha256()
    for part in parts:
        digest.update(part)
    return digest.digest()


def _hash_int(*parts: bytes) -> int:
    """Return the SHA-256 digest of the concatenated chunks as a big-endian integer."""
    return int.from_bytes(_hash(*parts), 'big')


def _pad(value: int) -> bytes:
    """Left-pad an integer to the byte length of `N` (the SRP `PAD` operation)."""
    return value.to_bytes(_N_BYTES, 'big')


# Multiplier parameter k = H(N | PAD(g)); fixed by the group, computed once.
_k: int = _hash_int(_pad(_N), _pad(_g))


def _random_exponent() -> int:
    """Return a fresh private exponent in `[1, N)` for an ephemeral key."""
    return 1 + secrets.randbelow(_N - 1)


def _derive_x(salt: bytes, email: str, password: str) -> int:
    """Derive the private exponent `x = H(salt | H(email ":" password))` (RFC 5054)."""
    inner: bytes = _hash(f'{email}:{password}'.encode())
    return _hash_int(salt, inner)


def _compute_u(client_public: int, server_public: int) -> int:
    """Compute the scrambling parameter `u = H(PAD(A) | PAD(B))`, rejecting `u == 0`."""
    u: int = _hash_int(_pad(client_public), _pad(server_public))
    if u == 0:
        raise ValueError('SRP handshake failed: u must not be zero')
    return u


def _session_key(shared: int) -> bytes:
    """Derive the shared session key `K = H(PAD(S))` from the premaster secret `S`."""
    return _hash(_pad(shared))


def _client_proof(email: str, salt: bytes, client_public: int, server_public: int, session_key: bytes) -> bytes:
    """Compute the client proof `M1 = H(H(N) XOR H(g) | H(email) | salt | PAD(A) | PAD(B) | K)`."""
    h_n: int = _hash_int(_pad(_N))
    h_g: int = _hash_int(_pad(_g))
    prefix: bytes = (h_n ^ h_g).to_bytes(sha256().digest_size, 'big')
    return _hash(prefix, _hash(email.encode()), salt,
                 _pad(client_public), _pad(server_public), session_key)


def _server_proof(client_public: int, client_proof: bytes, session_key: bytes) -> bytes:
    """Compute the server proof `M2 = H(PAD(A) | M1 | K)`."""
    return _hash(_pad(client_public), client_proof, session_key)


def compute_verifier(salt: bytes, email: str, password: str) -> int:
    """Compute the SRP verifier `v = g**x mod N` for the given salt and credentials."""
    return pow(_g, _derive_x(salt, email, password), _N)


class SrpToken(NamedTuple):
    """The server's stored secret for one user: the salt and password verifier.

    Serialised to `<version>$<salt-hex>$<verifier-hex>`; the on-disk user store
    keeps the salt and verifier as separate hex fields but round-trips through
    this type.
    """

    salt: bytes
    verifier: int

    @classmethod
    def create(cls, email: str, password: str, *, salt: bytes | None = None) -> SrpToken:
        """Mint a token from credentials, generating a random salt when none is supplied."""
        salt = salt if salt is not None else secrets.token_bytes(_SALT_BYTES)
        return cls(salt=salt, verifier=compute_verifier(salt, email, password))

    @classmethod
    def parse(cls, token: str) -> SrpToken:
        """Parse a serialised token, raising ValueError if it is malformed or a foreign version."""
        try:
            version, salt_hex, verifier_hex = token.split('$')
        except ValueError as exc:
            raise ValueError('malformed srp token') from exc
        if version != VERSION:
            raise ValueError(f'unsupported srp token version: {version!r}')
        return cls(salt=bytes.fromhex(salt_hex), verifier=int(verifier_hex, 16))

    def serialize(self) -> str:
        """Serialise to the `<version>$<salt-hex>$<verifier-hex>` storage form."""
        return f'{VERSION}${self.salt.hex()}${self.verifier:x}'

    def __str__(self) -> str:
        """Return a truncated, non-secret-leaking summary."""
        return f'{self.__class__.__name__}(salt={self.salt.hex()}, verifier={self.verifier:x}'[:48] + '...)'


def make_srp_token(email: str, password: str, *, salt: bytes | None = None) -> str:
    """Mint and serialise an SRP token for `(email, password)` — the storage entry point."""
    return SrpToken.create(email, password, salt=salt).serialize()


class SrpClient:
    """The client side of an SRP-6a handshake: knows the password, proves it to the server."""

    def __init__(self, email: str, password: str) -> None:
        self.email: str = email
        self._password: str = password
        self._a: int = _random_exponent()
        #: The client's ephemeral public value `A = g**a mod N` (sent to the server).
        self.public: int = pow(_g, self._a, _N)
        self._session_key: bytes | None = None
        self._proof: bytes | None = None

    def process_challenge(self, salt: bytes, server_public: int) -> bytes:
        """Consume the server's `salt` and public `B`, returning the client proof `M1`.

        Raises:
            ValueError: If `B` is invalid (`B mod N == 0`).
        """
        if server_public % _N == 0:
            raise ValueError('SRP handshake failed: server public value B is invalid')
        x: int = _derive_x(salt, self.email, self._password)
        u: int = _compute_u(self.public, server_public)
        # S = (B - k * g**x) ** (a + u * x) mod N
        shared: int = pow(server_public - _k * pow(_g, x, _N), self._a + u * x, _N)
        self._session_key = _session_key(shared)
        self._proof = _client_proof(self.email, salt, self.public, server_public, self.session_key)
        return self.proof

    def verify_session(self, server_proof: bytes) -> bool:
        """Return True if the server's proof `M2` matches, confirming a shared session key."""
        if self._session_key is None or self._proof is None:
            raise ValueError('process_challenge must be called before verify_session')
        expected: bytes = _server_proof(self.public, self._proof, self._session_key)
        return secrets.compare_digest(expected, server_proof)

    @property
    def session_key(self) -> bytes:
        """The negotiated shared key `K` (available only after :meth:`process_challenge`)."""
        if self._session_key is None:
            raise ValueError('process_challenge must be called before the session key is available')
        return self._session_key

    @property
    def proof(self) -> bytes:
        """The client proof `M1` (available only after :meth:`process_challenge`)."""
        if self._proof is None:
            raise ValueError('process_challenge must be called before the proof is available')
        return self._proof


class SrpServer:
    """The server side of an SRP-6a handshake: holds the verifier, validates the client proof."""

    def __init__(self, email: str, token: SrpToken) -> None:
        self.email: str = email
        self._token: SrpToken = token
        self._b: int = _random_exponent()
        # B = (k * v + g**b) mod N
        #: The server's ephemeral public value `B` (sent to the client with the salt).
        self.public: int = (_k * token.verifier + pow(_g, self._b, _N)) % _N
        self._session_key: bytes | None = None

    @property
    def salt(self) -> bytes:
        """The stored salt to send to the client alongside `B`."""
        return self._token.salt

    def verify(self, client_public: int, client_proof: bytes) -> bytes:
        """Validate the client's public `A` and proof `M1`; return the server proof `M2`.

        Raises:
            ValueError: If `A` is invalid (`A mod N == 0`) or the proof does not match
                        (wrong password).
        """
        if client_public % _N == 0:
            raise ValueError('SRP handshake failed: client public value A is invalid')
        u: int = _compute_u(client_public, self.public)
        # S = (A * v**u) ** b mod N
        shared: int = pow(client_public * pow(self._token.verifier, u, _N), self._b, _N)
        self._session_key = _session_key(shared)
        expected: bytes = _client_proof(self.email, self._token.salt, client_public, self.public, self.session_key)
        if not secrets.compare_digest(expected, client_proof):
            raise ValueError('SRP handshake failed: bad client proof (wrong password)')
        return _server_proof(client_public, client_proof, self.session_key)

    @property
    def session_key(self) -> bytes:
        """The negotiated shared key `K` (available only after a successful :meth:`verify`)."""
        if self._session_key is None:
            raise ValueError('verify must succeed before the session key is available')
        return self._session_key


def verify_password(email: str, password: str, token: SrpToken) -> bool:
    """Return True if `password` matches the verifier in `token` for `email`.

    Runs a complete SRP-6a handshake locally (client with the supplied password,
    server with the stored verifier), exercising exactly the same code paths a
    remote, zero-knowledge client would drive. Any handshake failure (i.e. a
    wrong password) yields False rather than raising.
    """
    server: SrpServer = SrpServer(email, token)
    client: SrpClient = SrpClient(email, password)
    try:
        client_proof: bytes = client.process_challenge(server.salt, server.public)
        server.verify(client.public, client_proof)
    except ValueError:
        return False
    return True
