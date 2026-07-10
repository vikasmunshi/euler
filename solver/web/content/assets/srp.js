/* SRP-6a browser client for the euler auth service.
 *
 * Interoperates byte-for-byte with solver/web/auth/srp.py: RFC 5054 2048-bit
 * group, g = 2, SHA-256 throughout, and every integer fed to the hash (A, B,
 * S, N, g) left-padded to the byte length of N (256 bytes). The email is
 * normalised (trim + lowercase) exactly like the server's store key.
 *
 * The password never leaves the browser: registration derives {salt, verifier}
 * locally, login runs the zero-knowledge handshake. Plain script (no modules,
 * CSP 'self'); exposes a single global `SRP`. Also loadable under Node for the
 * repo's interop tests.
 */
'use strict';

const SRP = (() => {
  const N_HEX =
    'AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050' +
    'A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50' +
    'E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B8' +
    '55F97993EC975EEAA80D740ADBF4FF747359D041D5C33EA71D281E446B14773B' +
    'CA97B43A23FB801676BD207A436C6481F1D2B9078717461A5B9D32E688F87748' +
    '544523B524B0D57D5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6' +
    'AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6' +
    '94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F9E4AFF73';
  const N = BigInt('0x' + N_HEX);
  const g = 2n;
  const N_BYTES = 256;
  const SALT_BYTES = 16;

  const subtle = globalThis.crypto.subtle;

  // ── byte/int helpers ─────────────────────────────────────────────────────────
  const te = new TextEncoder();

  function concat(...parts) {
    const total = parts.reduce((n, p) => n + p.length, 0);
    const out = new Uint8Array(total);
    let offset = 0;
    for (const p of parts) { out.set(p, offset); offset += p.length; }
    return out;
  }

  function bytesToHex(bytes) {
    return Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
  }

  function hexToBytes(hex) {
    if (hex.length % 2) hex = '0' + hex;
    const out = new Uint8Array(hex.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.slice(2 * i, 2 * i + 2), 16);
    return out;
  }

  function bytesToInt(bytes) { return BigInt('0x' + (bytesToHex(bytes) || '0')); }

  // Left-pad an integer to the byte length of N (the SRP PAD operation).
  function pad(value) {
    const hex = value.toString(16).padStart(N_BYTES * 2, '0');
    return hexToBytes(hex);
  }

  async function hash(...parts) {
    return new Uint8Array(await subtle.digest('SHA-256', concat(...parts)));
  }

  async function hashInt(...parts) { return bytesToInt(await hash(...parts)); }

  function modPow(base, exp, mod) {
    base %= mod;
    let result = 1n;
    while (exp > 0n) {
      if (exp & 1n) result = (result * base) % mod;
      base = (base * base) % mod;
      exp >>= 1n;
    }
    return result;
  }

  function randomInt(bytes) {
    const buf = new Uint8Array(bytes);
    globalThis.crypto.getRandomValues(buf);
    return bytesToInt(buf);
  }

  function normalizeEmail(email) { return email.trim().toLowerCase(); }

  // x = H(salt | H(email ":" password))  (RFC 5054)
  async function deriveX(saltBytes, email, password) {
    const inner = await hash(te.encode(`${email}:${password}`));
    return hashInt(saltBytes, inner);
  }

  // ── registration: derive {salt, verifier} locally ───────────────────────────
  async function computeVerifier(email, password) {
    const norm = normalizeEmail(email);
    const salt = new Uint8Array(SALT_BYTES);
    globalThis.crypto.getRandomValues(salt);
    const x = await deriveX(salt, norm, password);
    const v = modPow(g, x, N);
    return { salt: bytesToHex(salt), verifier: v.toString(16) };
  }

  // ── login: the zero-knowledge handshake ──────────────────────────────────────
  // Usage: const c = await SRP.startLogin(email, password);
  //        POST /auth/challenge {email} -> {salt, B}
  //        const {A, M1, check} = await c.respond(salt, B);
  //        POST /auth/verify {email, A, M1} -> {M2}; await check(M2) must be true.
  async function startLogin(email, password) {
    const norm = normalizeEmail(email);
    let a = 0n;
    while (a === 0n) a = randomInt(32) % (N - 1n) + 1n;
    const A = modPow(g, a, N);
    const k = await hashInt(pad(N), pad(g));

    async function respond(saltHex, bHex) {
      const B = BigInt('0x' + bHex);
      if (B % N === 0n) throw new Error('SRP: invalid server value B');
      const salt = hexToBytes(saltHex);
      const u = await hashInt(pad(A), pad(B));
      if (u === 0n) throw new Error('SRP: u must not be zero');
      const x = await deriveX(salt, norm, password);
      // S = (B - k * g**x) ** (a + u * x) mod N   (keep the base non-negative)
      const base = ((B - k * modPow(g, x, N)) % N + N) % N;
      const S = modPow(base, a + u * x, N);
      const K = await hash(pad(S));
      const hN = await hash(pad(N));
      const hG = await hash(pad(g));
      const prefix = hN.map((b, i) => b ^ hG[i]);
      const M1 = await hash(prefix, await hash(te.encode(norm)), salt, pad(A), pad(B), K);
      const expectedM2 = await hash(pad(A), M1, K);

      return {
        A: A.toString(16),
        M1: bytesToHex(M1),
        M2: bytesToHex(expectedM2),  // what the server must prove back
        // Verify the server proof M2 — mutual authentication.
        check: (m2Hex) => bytesToHex(expectedM2) === m2Hex.toLowerCase(),
      };
    }

    return { email: norm, respond };
  }

  return { computeVerifier, startLogin, normalizeEmail };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = SRP;  // node (tests)
