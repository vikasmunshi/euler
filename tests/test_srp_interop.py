#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""JS ↔ Python SRP-6a interop: the browser client (packages/site/euler_site/content/assets/srp.js)
against the service's srp.py, byte-for-byte (RFC 5054 2048-bit group, SHA-256,
PAD to |N|), for both password hashes inside `x` — Argon2id (the vendored hash-wasm in the
browser, argon2-cffi here) and the legacy SHA-256 — and for the upgrade from one to the other.
Skips when Node.js is absent — install it with `make install-nodejs`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from euler_site.auth.srp import KDF, KDF_LEGACY, SrpClient, SrpServer, SrpToken, compute_verifier

REPO = Path(__file__).resolve().parent.parent
SRP_JS = REPO / 'packages' / 'site' / 'euler_site' / 'content' / 'assets' / 'srp.js'

_DRIVER = """\
const SRP = require(process.argv[2]);
const [mode, ...args] = process.argv.slice(3);
(async () => {
  if (mode === 'register') {
    const [email, password] = args;
    console.log(JSON.stringify(await SRP.computeVerifier(email, password)));
  } else if (mode === 'upgrade') {
    const [email, password, salt] = args;
    console.log(JSON.stringify({ verifier: await SRP.upgradeVerifier(email, password, salt) }));
  } else if (mode === 'constants') {
    console.log(JSON.stringify({ KDF: SRP.KDF, KDF_LEGACY: SRP.KDF_LEGACY }));
  } else {
    const [email, password, salt, B, kdf] = args;
    const c = await SRP.startLogin(email, password);
    const r = await c.respond(salt, B, kdf);
    console.log(JSON.stringify({ A: r.A, M1: r.M1, M2: r.M2 }));
  }
})().catch(e => { console.error(e); process.exit(1); });
"""

EMAIL = '  Alice@Example.COM '            # exercises trim + lowercase normalisation
NORM = 'alice@example.com'
PASSWORD = 'Correct-Horse-Battery-42!Ω'  # non-ASCII exercises UTF-8 hashing


def _find_node() -> str | None:
    node = shutil.which('node')
    if node:
        return node
    candidates = sorted(Path.home().glob('.local/opt/node-*/bin/node'))
    return str(candidates[-1]) if candidates else None


@unittest.skipIf(_find_node() is None, 'node not installed (make install-nodejs)')
class SrpInteropTest(unittest.TestCase):
    """Drive the real browser asset under Node against the Python server."""

    node: str
    driver: Path

    @classmethod
    def setUpClass(cls) -> None:
        node = _find_node()
        assert node is not None            # guarded by the skipIf decorator
        cls.node = node
        cls.driver = Path(tempfile.mkstemp(suffix='.js')[1])
        cls.driver.write_text(_DRIVER, encoding='utf-8')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.unlink(missing_ok=True)

    def _node(self, *args: str) -> dict[str, str]:
        out = subprocess.run([self.node, str(self.driver), str(SRP_JS), *args],
                             capture_output=True, text=True, check=True)
        result: dict[str, str] = json.loads(out.stdout.strip())
        self.assertIsInstance(result, dict)
        return result

    def test_full_interop(self) -> None:
        # 1. Browser-side registration: {salt, verifier} derived in JS.
        reg = self._node('register', EMAIL, PASSWORD)
        self.assertEqual(reg['kdf'], KDF, 'a new verifier uses the current password hash')
        token = SrpToken(salt=bytes.fromhex(reg['salt']), verifier=int(reg['verifier'], 16), kdf=reg['kdf'])

        # 2. The Python client must authenticate against the JS-minted verifier.
        server = SrpServer(NORM, token)
        client = SrpClient(NORM, PASSWORD)
        proof = client.process_challenge(server.salt, server.public)
        self.assertTrue(client.verify_session(server.verify(client.public, proof)))

        # 3. The JS client must authenticate against the Python server (mutual).
        server = SrpServer(NORM, token)
        js = self._node('login', EMAIL, PASSWORD, server.salt.hex(), f'{server.public:x}', KDF)
        m2 = server.verify(int(js['A'], 16), bytes.fromhex(js['M1']))
        self.assertEqual(m2.hex(), js['M2'])

        # 4. A wrong password must fail the handshake.
        server = SrpServer(NORM, token)
        bad = self._node('login', EMAIL, 'Wrong-Password-123!xyz',
                         server.salt.hex(), f'{server.public:x}', KDF)
        with self.assertRaises(ValueError):
            server.verify(int(bad['A'], 16), bytes.fromhex(bad['M1']))

    def test_a_legacy_account_signs_in_and_upgrades(self) -> None:
        """An account minted before Argon2 still signs in from the browser, and the verifier
        the browser sends to upgrade it is the one Python derives for the same salt."""
        legacy = SrpToken.create(NORM, PASSWORD)._replace(kdf=KDF_LEGACY)
        legacy = legacy._replace(verifier=compute_verifier(legacy.salt, NORM, PASSWORD, KDF_LEGACY))
        server = SrpServer(NORM, legacy)
        js = self._node('login', EMAIL, PASSWORD, server.salt.hex(), f'{server.public:x}', KDF_LEGACY)
        self.assertEqual(server.verify(int(js['A'], 16), bytes.fromhex(js['M1'])).hex(), js['M2'])

        upgraded = self._node('upgrade', EMAIL, PASSWORD, legacy.salt.hex())
        self.assertEqual(int(upgraded['verifier'], 16), compute_verifier(legacy.salt, NORM, PASSWORD, KDF))
        token = SrpToken(salt=legacy.salt, verifier=int(upgraded['verifier'], 16), kdf=KDF)
        server = SrpServer(NORM, token)
        js = self._node('login', EMAIL, PASSWORD, server.salt.hex(), f'{server.public:x}', KDF)
        self.assertEqual(server.verify(int(js['A'], 16), bytes.fromhex(js['M1'])).hex(), js['M2'])

    def test_both_ends_name_the_same_password_hashes(self) -> None:
        self.assertEqual(self._node('constants'), {'KDF': KDF, 'KDF_LEGACY': KDF_LEGACY})


if __name__ == '__main__':
    unittest.main()
