#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.srp (SRP-6a).

Includes the **cross-implementation reference vectors**: fixed values a future
browser-side SRP client must reproduce byte-for-byte to interoperate. If the
group, hash, PAD, or proof construction ever changes, these break — which is the
point. Regenerate deliberately (and update the JS client to match) only when the
protocol version is intentionally bumped.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from solver.web.auth import srp

# --- Reference vectors (see docstring) -------------------------------------
_EMAIL = 'user@example.com'
_PASSWORD = 'correct horse battery staple'
_SALT = bytes.fromhex('00112233445566778899aabbccddeeff')

# Deterministic (no ephemerals): x and verifier from (salt, email, password).
_X_HEX = '878c407848170e1232250a06d28d234111edf4dfe899889c221a7978fd4b838d'
_VERIFIER_HEX = (
    '412cadf21c82bd3c7659cfa6c9112ab5b25cb744b873fc6e7cb6df3088158525'
    'f75b42c21285d7292b74ce7a51160b57ea635cac09242afcbc428df10e80111f'
    'c791398d33dc630640fb2d020b16e50bb2dcb2d70c2f739a5800203e1e808eeb'
    '594a3ed25d4fd0e7d0445f971e9740c7dc17c6a68b3c5047df2d74ffa4ba6823'
    '6fee5e636ca19256b5af5d819e487750e52528efa880ec2cf46faa6730e79d1b'
    '9ec9dce85166a83b380887bb0590847fe61ae5a666b4da6d08dc8f2a97fd7cbc'
    '6c32651284adcee46e08acee4605e9e866b18af31536de4da47060fe0c2252cd'
    'aa67a050cf839217a5ac79655afefb407d1c5be7595528f16af072aa20f1337e')

# Fixed-ephemeral full handshake (server built first with b, then client with a).
_A_EXP = int('deadbeef' * 8, 16)
_B_EXP = int('feedface' * 8, 16)
_A_HEX = (
    '61e5a51ed7b9e8bf100c40e319cf6f6891f6ac7119fa1f5e959614a378e9fe1b'
    'bd7071192ef0e8f2c22664e4547bfd7200cce038c66fd1b27ccbb9f87c098530'
    '0466ef03b02b0e538a3bcdfb34f28fb8dcb2c9c96c22ba2547d5ab0669b39ebe'
    'ac057285a98b6bd401f390b3b5f7d13ee71baa47bddd70d0a4f5069347e99f58'
    'addaf7ca8888bc453fe8a7e041ffe7ca1f1cb74daaee1260ff004d424d3f5bdd'
    'c1e235c3e792fb8d90bdd3f0f944b38e28f9a8cb6f50a3f6d99a7c58c60ffe86'
    'e1f9a33c2ee10e40997b45f77b1bcc215fa1b560b0fb400c2df94d1b38aa997d'
    '797dec940466ae9191f9ce8e34cf791a75a83161280d7f0b196c5bb0cfd3a37d')
_B_HEX = (
    'f59f2d65fb89b5c26b2a83763f79670f25c2b7251f5e751ac5be6193e200f462'
    '50ef66721c6be18755c4a27e1dc9f13dca8e1b76e2e394b5a51bcfdf65ea112f'
    '9a3a22f3043b1dd69afc0efbb147393ec58141d33c92e0b2fa86c9f491792b65'
    '9628a8a59fb174ae34a75a37ba107d2356582e01362a1cbc80a05308a8dc47cb'
    '528724c19faa8df95c1d89102b85cfef8d5703d791034d951a9e22be2ee5a342'
    '896fe908e6db5ab8930b2a9bae2f7de5b4016fe88a07ea0a0f4bdb937ca0b795'
    '77e87c7cc83b861ec1cb8ff9927e90e654b590862b19a584e2dea2207f73e232'
    '727814c66dc391107d6940726d31b8134f3ca7ac3c172abcf061e37301b370f')
_M1_HEX = '246d0effd76fb2c58b41fcf73c8b1bab1329ce6bca190efb639a21edf6e91df7'
_M2_HEX = '660f648df00840decddece5c403a6a80f50b801607212c109f7135a386393fb2'
_K_HEX = 'fbe681f3f72b005e752c66a5360d0965708074d1b0d602393622a0657f459e80'


class ReferenceVectorTests(unittest.TestCase):
    """Lock the byte-exact protocol behaviour for JS interop."""

    def test_derive_x_and_verifier(self) -> None:
        self.assertEqual(format(srp._derive_x(_SALT, _EMAIL, _PASSWORD), 'x'), _X_HEX)
        self.assertEqual(format(srp.compute_verifier(_SALT, _EMAIL, _PASSWORD), 'x'), _VERIFIER_HEX)

    def test_fixed_ephemeral_handshake(self) -> None:
        token = srp.SrpToken(salt=_SALT, verifier=int(_VERIFIER_HEX, 16))
        with patch.object(srp, '_random_exponent', side_effect=[_B_EXP, _A_EXP]):
            server = srp.SrpServer(_EMAIL, token)   # consumes _B_EXP
            client = srp.SrpClient(_EMAIL, _PASSWORD)  # consumes _A_EXP
            m1 = client.process_challenge(server.salt, server.public)
            m2 = server.verify(client.public, m1)
        self.assertEqual(format(client.public, 'x'), _A_HEX)
        self.assertEqual(format(server.public, 'x'), _B_HEX)
        self.assertEqual(m1.hex(), _M1_HEX)
        self.assertEqual(m2.hex(), _M2_HEX)
        self.assertEqual(client.session_key.hex(), _K_HEX)
        self.assertEqual(server.session_key.hex(), _K_HEX)
        self.assertTrue(client.verify_session(m2))


class HandshakeTests(unittest.TestCase):
    """End-to-end SRP behaviour with random ephemerals."""

    def _run(self, reg_pw: str, login_pw: str) -> bool:
        token = srp.SrpToken.create(_EMAIL, reg_pw)
        server = srp.SrpServer(_EMAIL, token)
        client = srp.SrpClient(_EMAIL, login_pw)
        m1 = client.process_challenge(server.salt, server.public)
        m2 = server.verify(client.public, m1)
        return client.verify_session(m2)

    def test_correct_password_succeeds(self) -> None:
        self.assertTrue(self._run('hunter2-correct-horse', 'hunter2-correct-horse'))

    def test_shared_key_matches(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'pw')
        server, client = srp.SrpServer(_EMAIL, token), srp.SrpClient(_EMAIL, 'pw')
        m1 = client.process_challenge(server.salt, server.public)
        server.verify(client.public, m1)
        self.assertEqual(client.session_key, server.session_key)

    def test_wrong_password_raises_on_verify(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'right')
        server = srp.SrpServer(_EMAIL, token)
        client = srp.SrpClient(_EMAIL, 'wrong')
        m1 = client.process_challenge(server.salt, server.public)
        with self.assertRaises(ValueError):
            server.verify(client.public, m1)

    def test_verify_password_helper(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'sekret')
        self.assertTrue(srp.verify_password(_EMAIL, 'sekret', token))
        self.assertFalse(srp.verify_password(_EMAIL, 'nope', token))

    def test_rejects_degenerate_public_values(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'pw')
        server = srp.SrpServer(_EMAIL, token)
        with self.assertRaises(ValueError):
            server.verify(0, b'\x00' * 32)          # A mod N == 0
        client = srp.SrpClient(_EMAIL, 'pw')
        with self.assertRaises(ValueError):
            client.process_challenge(token.salt, 0)  # B mod N == 0


class TokenSerializationTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'pw', salt=_SALT)
        parsed = srp.SrpToken.parse(token.serialize())
        self.assertEqual(parsed, token)

    def test_serialize_shape(self) -> None:
        serialized = srp.make_srp_token(_EMAIL, 'pw', salt=_SALT)
        version, salt_hex, _verifier_hex = serialized.split('$')
        self.assertEqual(version, srp.VERSION)
        self.assertEqual(salt_hex, _SALT.hex())

    def test_bad_version_rejected(self) -> None:
        with self.assertRaises(ValueError):
            srp.SrpToken.parse('srp6a-sha1-1024$00$ff')

    def test_malformed_rejected(self) -> None:
        with self.assertRaises(ValueError):
            srp.SrpToken.parse('not-a-token')

    def test_str_does_not_leak_full_verifier(self) -> None:
        token = srp.SrpToken.create(_EMAIL, 'pw', salt=_SALT)
        self.assertNotIn(format(token.verifier, 'x'), str(token))


if __name__ == '__main__':
    unittest.main()
