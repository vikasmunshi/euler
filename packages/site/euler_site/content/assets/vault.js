/* Vault client: derive the password key PK in the browser and drive
 * the per-user service's vault endpoints. The password never leaves the browser —
 * PK = Argon2id(password, "euler-vault-pk:" | SRP salt), from the vendored hash-wasm
 * (base.html loads it first), is sent only to the signed-in user's OWN service (same
 * origin, TLS), which unwraps the vault key with it. PK can unwrap VK, so it is
 * handled as a secret: kept in sessionStorage (this tab only, gone when the tab closes),
 * never logged, never sent anywhere else. Loaded on every page through base.html (the
 * sign-in form, auto-unlock, account-panel recovery). CSP-clean; Node-loadable for the
 * interop tests. */
'use strict';

(() => {
  if (globalThis.Vault) return;   // idempotent across htmx fragment re-injection

  // Keep in sync with packages/solver/solver/crypto/wire.py: VAULT_KDF and VAULT_ARGON2_LABEL
  // (tests/test_srp_interop.py pins them).
  const KDF = 'argon2id$m=65536,t=3,p=1';
  const ARGON2_LABEL = 'euler-vault-pk:';
  const PK_KEY = 'euler.vault.pk';
  const SALT_KEY = 'euler.vault.salt';

  const hexToBytes = (hex) =>
    Uint8Array.from(hex.match(/../g).map((h) => parseInt(h, 16)));

  function argon2() {
    if (globalThis.hashwasm) return globalThis.hashwasm;
    return typeof require === 'function' ? require('../vendor/hash-wasm/argon2.umd.min.js') : null;
  }

  /* PK from the password + salt: Argon2id with kdf's parameters (default: the current ones) —
   * identical to the server's derive_password_key. */
  async function derivePk(password, saltHex, kdf) {
    const encoded = new TextEncoder().encode(password);
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

  /* PK for an existing vault, with its own recorded parameters: `info` is /vault/status's body. */
  function derivePkFor(password, info) {
    return derivePk(password, info.salt, info.kdf);
  }

  function store(pkHex, saltHex) {
    try {
      sessionStorage.setItem(PK_KEY, pkHex);
      sessionStorage.setItem(SALT_KEY, saltHex);
    } catch (e) { /* private mode: unlock simply won't be automatic */ }
  }

  function stored() {
    try {
      const pk = sessionStorage.getItem(PK_KEY);
      const salt = sessionStorage.getItem(SALT_KEY);
      return pk && salt ? { pk, salt } : null;
    } catch (e) { return null; }
  }

  function clear() {
    try {
      sessionStorage.removeItem(PK_KEY);
      sessionStorage.removeItem(SALT_KEY);
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
      const resp = await postJson('/vault/unlock', { pk: creds.pk, salt: creds.salt });
      if (resp.ok) return 'unlocked';
      return resp.status === 409 ? 'stale' : 'error';
    } catch (e) {
      return 'error';
    }
  }

  globalThis.Vault = { derivePk, derivePkFor, store, stored, clear, unlock, postJson, KDF };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = globalThis.Vault;  // node (tests)
