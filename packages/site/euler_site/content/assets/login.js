/* Sign-in page: drive the SRP-6a handshake against the auth service.
 * The password never leaves the browser; the server proves itself back (M2). */
'use strict';

(() => {
  const form = document.getElementById('login-form');
  if (!form) return;
  const errorBox = document.getElementById('form-error');
  const submit = document.getElementById('submit-btn');
  const submitLabel = document.getElementById('submit-label');
  const password = document.getElementById('password');

  // The submit button's two states: idle "sign in", and "proving…" while the
  // SRP handshake is in flight (the one moment the box has nothing to show).
  function busy(on) {
    submit.disabled = on;
    submit.classList.toggle('busy', on);
    if (submitLabel) submitLabel.textContent = on ? 'proving…' : 'sign in';
  }

  function fail(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    busy(false);
  }
  // The reveal toggle and caps-lock warning are wired by authform.js (shared
  // with the register page); this file owns only the SRP handshake.

  async function post(path, body) {
    return fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body),
    });
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    busy(true);
    const email = document.getElementById('email').value;
    const secret = password.value;
    const remember = document.getElementById('remember').checked;
    try {
      const client = await SRP.startLogin(email, secret);
      const challenge = await post('/auth/challenge', { email: client.email });
      if (!challenge.ok) return fail('Sign-in failed. Check your email and password.');
      const { salt, B } = await challenge.json();
      const proof = await client.respond(salt, B);
      const verify = await post('/auth/verify',
                                { email: client.email, A: proof.A, M1: proof.M1, remember });
      if (!verify.ok) return fail('Sign-in failed. Check your email and password.');
      const { M2 } = await verify.json();
      if (!proof.check(M2)) return fail('Server failed mutual authentication — not signing in.');
      // Vault: derive PK from the password we still hold and the SRP
      // salt, for the per-user service to unlock the vault with. Best-effort — a
      // failure only means the vault stays locked (the account panel can recover).
      try {
        if (window.Vault) Vault.store(await Vault.derivePk(secret, salt), salt);
      } catch (err) { /* vault stays locked */ }
      window.location.replace('/');
    } catch (err) {
      fail('Sign-in failed: ' + (err && err.message ? err.message : 'unexpected error'));
    }
  });
})();
