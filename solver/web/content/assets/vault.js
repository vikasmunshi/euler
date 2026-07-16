/* Vault client: derive the password key PK in the browser and drive
 * the per-user service's vault endpoints. The password never leaves the browser —
 * PK = PBKDF2-HMAC-SHA256(password, SRP salt) is derived with WebCrypto and sent
 * only to the signed-in user's OWN service (same origin, TLS), which unwraps the
 * vault key with it. PK can unwrap VK, so it is handled as a secret: kept in
 * sessionStorage (this tab only, gone when the tab closes), never logged, never
 * sent anywhere else. Loaded on the auth pages (derivation at sign-in) and the
 * content shell (auto-unlock, account-panel recovery). No deps, CSP-clean. */
'use strict';

(() => {
  if (window.Vault) return;   // idempotent across htmx fragment re-injection

  // Keep in sync with solver/crypto/config.py vault_kdf_iterations (the OWASP
  // floor for PBKDF2-SHA256). An older vault's own count arrives via /vault/status.
  const ITERATIONS = 600000;
  const PK_KEY = 'euler.vault.pk';
  const SALT_KEY = 'euler.vault.salt';

  const bytesToHex = (bytes) =>
    Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
  const hexToBytes = (hex) =>
    Uint8Array.from(hex.match(/../g).map((h) => parseInt(h, 16)));

  /* PK from the password + salt — identical to the server's derive_password_key. */
  async function derivePk(password, saltHex, iterations) {
    const material = await crypto.subtle.importKey(
      'raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
    const bits = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', hash: 'SHA-256', salt: hexToBytes(saltHex),
        iterations: iterations || ITERATIONS },
      material, 256);
    return bytesToHex(new Uint8Array(bits));
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

  window.Vault = { derivePk, store, stored, clear, unlock, postJson, ITERATIONS };
})();
