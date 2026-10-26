/* Vault client: derive the password key PK in the browser and drive
 * the per-user service's vault endpoints. The password never leaves the browser —
 * PK = Argon2id(password, "euler-vault-pk:" | SRP salt), from the vendored hash-wasm
 * (base.html loads it first), is sent only to the signed-in user's OWN service (same
 * origin, TLS), which unwraps the vault key with it. A vault made before Argon2 is
 * PBKDF2-SHA256 (WebCrypto); sign-in derives that key too, and the service uses it once
 * to move the vault to Argon2id (`legacy_pk`, /vault/unlock). PK can unwrap VK, so it is
 * handled as a secret: kept in sessionStorage (this tab only, gone when the tab closes),
 * never logged, never sent anywhere else. Loaded on every page through base.html (the
 * sign-in form, auto-unlock, account-panel recovery). CSP-clean; Node-loadable for the
 * interop tests. */
'use strict';

(() => {
  if (globalThis.Vault) return;   // idempotent across htmx fragment re-injection

  // Keep in sync with packages/solver/solver/crypto/wire.py: VAULT_KDF, VAULT_ARGON2_LABEL,
  // VAULT_KDF_LEGACY and VAULT_KDF_ITERATIONS (tests/test_srp_interop.py pins them).
  const KDF = 'argon2id$m=65536,t=3,p=1';
  const KDF_LEGACY = 'pbkdf2-sha256';
  const ARGON2_LABEL = 'euler-vault-pk:';
  const ITERATIONS = 600000;
  const PK_KEY = 'euler.vault.pk';
  const SALT_KEY = 'euler.vault.salt';
  const LEGACY_KEY = 'euler.vault.legacy-pk';

  const bytesToHex = (bytes) =>
    Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
  const hexToBytes = (hex) =>
    Uint8Array.from(hex.match(/../g).map((h) => parseInt(h, 16)));

  function argon2() {
    if (globalThis.hashwasm) return globalThis.hashwasm;
    return typeof require === 'function' ? require('../vendor/hash-wasm/argon2.umd.min.js') : null;
  }

  /* PK from the password + salt, by kdf (default: the current one) — identical to the
   * server's derive_password_key. */
  async function derivePk(password, saltHex, kdf, iterations) {
    const encoded = new TextEncoder().encode(password);
    if ((kdf || KDF) === KDF_LEGACY) {
      const material = await crypto.subtle.importKey('raw', encoded, 'PBKDF2', false, ['deriveBits']);
      const bits = await crypto.subtle.deriveBits(
        { name: 'PBKDF2', hash: 'SHA-256', salt: hexToBytes(saltHex),
          iterations: iterations || ITERATIONS },
        material, 256);
      return bytesToHex(new Uint8Array(bits));
    }
    const params = /^argon2id\$m=(\d+),t=(\d+),p=(\d+)$/.exec(kdf || KDF);
    if (!params) throw new Error('vault: unsupported password hash ' + kdf);
    const lib = argon2();
    if (!lib) throw new Error('vault: the Argon2 module did not load');
    const label = new TextEncoder().encode(ARGON2_LABEL);
    const salt = new Uint8Array(label.length + saltHex.length / 2);
    salt.set(label);
    salt.set(hexToBytes(saltHex), label.length);
    return lib.argon2id({
      password: encoded, salt, memorySize: Number(params[1]), iterations: Number(params[2]),
      parallelism: Number(params[3]), hashLength: 32, outputType: 'hex',
    });
  }

  /* PK for an existing vault, the way it was made: `info` is /vault/status's body. */
  function derivePkFor(password, info) {
    return derivePk(password, info.salt, info.kdf || KDF_LEGACY, info.iterations);
  }

  /* Keep this sign-in's PK (and, while vaults made before Argon2 remain, the PBKDF2 one
   * that opens such a vault once so the service can move it). */
  function store(pkHex, saltHex, legacyPkHex) {
    try {
      sessionStorage.setItem(PK_KEY, pkHex);
      sessionStorage.setItem(SALT_KEY, saltHex);
      if (legacyPkHex) sessionStorage.setItem(LEGACY_KEY, legacyPkHex);
      else sessionStorage.removeItem(LEGACY_KEY);
    } catch (e) { /* private mode: unlock simply won't be automatic */ }
  }

  function stored() {
    try {
      const pk = sessionStorage.getItem(PK_KEY);
      const salt = sessionStorage.getItem(SALT_KEY);
      const legacyPk = sessionStorage.getItem(LEGACY_KEY) || undefined;
      return pk && salt ? { pk, salt, legacyPk } : null;
    } catch (e) { return null; }
  }

  function clear() {
    try {
      sessionStorage.removeItem(PK_KEY);
      sessionStorage.removeItem(SALT_KEY);
      sessionStorage.removeItem(LEGACY_KEY);
    } catch (e) { /* nothing stored anyway */ }
  }

  async function postJson(path, body) {
    return fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body),
    });
  }

  /* Idempotent session unlock: 'unlocked' | 'no-pk' | 'stale' | 'error'.
   * First login initialises the vault server-side (the salt rides along). */
  async function unlock() {
    const creds = stored();
    if (!creds) return 'no-pk';
    try {
      const status = await fetch('/vault/status', { credentials: 'same-origin' });
      if (!status.ok) return 'error';
      if ((await status.json()).unlocked) return 'unlocked';
      const resp = await postJson('/vault/unlock',
        { pk: creds.pk, salt: creds.salt, legacy_pk: creds.legacyPk });
      if (resp.ok) {
        try { sessionStorage.removeItem(LEGACY_KEY); } catch (e) { /* nothing to drop */ }
        return 'unlocked';
      }
      return resp.status === 409 ? 'stale' : 'error';
    } catch (e) {
      return 'error';
    }
  }

  globalThis.Vault = { derivePk, derivePkFor, store, stored, clear, unlock, postJson,
                      KDF, KDF_LEGACY, ITERATIONS };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = globalThis.Vault;  // node (tests)
