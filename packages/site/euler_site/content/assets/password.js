/* Change-password (signed-in): prove the CURRENT password over SRP, then submit
 * the {salt, verifier} derived from the NEW one — neither password leaves the
 * browser. Distinct from the forgot/reset flow (no mailbox trip).
 *
 * Wires on both the standalone auth page (DOMContentLoaded) and the content
 * shell's left pane (htmx:afterSwap, when this script is re-injected with the
 * fragment). Idempotent: a form is wired once (dataset guard). On success it
 * re-keys the vault and then signs this session out too: the change already ended
 * every other session, and this one still holds the old vault key in its shell.
 * The next sign-in, with the new password, opens the re-keyed vault. */
'use strict';

(() => {
  const MIN_LENGTH = 16;   // keep in sync with packages/site/euler_site/auth/policy.py

  function policyError(password) {
    if (password.length < MIN_LENGTH) return `Use at least ${MIN_LENGTH} characters.`;
    const classes = [/[a-z]/, /[A-Z]/, /[0-9]/, /[^a-zA-Z0-9]/];
    if (!classes.every(re => re.test(password))) {
      return 'Use all four classes: lowercase, uppercase, digits, and specials.';
    }
    return null;
  }

  async function post(path, body) {
    return fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body),
    });
  }

  async function succeed() {
    // Sign out here as well, the same way the user menu does (forget PK, disarm the
    // terminal's leave-page guard), then land on the sign-in page, which returns to
    // /account. The sign-out is best-effort: the session is already the only one left,
    // and a failed POST still leaves the browser on the sign-in page.
    if (window.Vault) window.Vault.clear();
    const terminal = document.getElementById('terminal');
    if (terminal && terminal.contentWindow) {
      terminal.contentWindow.postMessage({ euler: 'disarm' }, window.location.origin);
    }
    try { await post('/auth/logout', {}); } catch (err) { /* landing on sign-in either way */ }
    window.location.replace('/login?next=' + encodeURIComponent('/account'));
  }

  function wire(form) {
    if (!form || form.dataset.wired) return;
    form.dataset.wired = '1';
    const errorBox = form.querySelector('#form-error');
    const submit = form.querySelector('#submit-btn');
    const fail = (message) => { errorBox.textContent = message; errorBox.hidden = false; submit.disabled = false; };

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      errorBox.hidden = true;
      submit.disabled = true;
      const current = form.querySelector('#current').value;
      const next = form.querySelector('#new1').value;
      const again = form.querySelector('#new2').value;
      if (next !== again) return fail('The new passwords do not match.');
      const problem = policyError(next);
      if (problem) return fail(problem);
      if (next === current) return fail('The new password must differ from the current one.');
      const email = form.dataset.email;
      try {
        // 1 · prove the current password (the same handshake as signing in)
        const client = await SRP.startLogin(email, current);
        const challenge = await post('/auth/challenge', { email: client.email });
        if (!challenge.ok) return fail('Could not start the change. Try again.');
        const { salt, B, id, kdf } = await challenge.json();
        const proof = await client.respond(salt, B, kdf);
        // 2 · derive the new credentials and swap them in one atomic exchange
        const derived = await SRP.computeVerifier(email, next);
        const change = await post('/auth/password', {
          A: proof.A, M1: proof.M1, id, salt: derived.salt, verifier: derived.verifier, kdf: derived.kdf,
        });
        if (change.status === 401) return fail('The current password is incorrect.');
        if (!change.ok) return fail('The change was refused. Try again.');
        const { M2 } = await change.json();
        if (!proof.check(M2)) return fail('Server failed mutual authentication — password unchanged? Sign in to verify.');
        // 3 · the secrets survive a password change, under a fresh vault key: re-key
        // the vault to the new password's PK. The old PK is derived the way the vault
        // was made (its kdf and salt, from /vault/status), so a vault from before Argon2
        // moves across too. Best-effort — no vault yet is made at the next sign-in; 409
        // means the vault was wrapped under something else (the account panel recovers).
        try {
          if (window.Vault) {
            const status = await fetch('/vault/status', { credentials: 'same-origin' });
            const info = status.ok ? await status.json() : { vault: false };
            if (info.vault) {
              const newPk = await Vault.derivePk(next, derived.salt);
              const oldPk = await Vault.derivePkFor(current, info);
              await Vault.postJson('/vault/rekey',
                { old_pk: oldPk, new_pk: newPk, new_salt: derived.salt });
            }
          }
        } catch (err) { /* recovery stays available on the account panel */ }
        await succeed();
      } catch (err) {
        fail('Change failed: ' + (err && err.message ? err.message : 'unexpected error'));
      }
    });
  }

  const init = () => wire(document.getElementById('password-form'));
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);   // standalone auth page
  } else {
    init();                                                // re-run per htmx swap
  }
  // Belt-and-suspenders for the in-shell case, registered once (the wire() guard
  // makes it idempotent even if the script also re-ran on the swap).
  if (window.htmx && !window.__pwAfterSwap) {
    window.__pwAfterSwap = true;
    document.body.addEventListener('htmx:afterSwap', init);
  }
})();
