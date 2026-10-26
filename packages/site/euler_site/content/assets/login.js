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

  // Where the reader lands. On /login: the page they came from — validated by the server
  // (auth/returnto.py) before it was written into the form; anything else was already `/`.
  // In the public site's right pane (data-next-here): the page the left pane shows now — the
  // header is not re-rendered as it moves, so only the live location knows. Reloaded with a
  // session, that same URL is served by the reader's own instance.
  function destination() {
    if (!form.hasAttribute('data-next-here')) return form.dataset.next || '/';
    const here = window.location.pathname + window.location.search;
    return here.charAt(0) === '/' && here.charAt(1) !== '/' ? here : '/';
  }

  async function post(path, body) {
    return fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body),
    });
  }

  // Remember me: the browser holds a token the server can redeem for a fresh session with no
  // password (the page marks the form data-resume; the cookie itself is HttpOnly). Tried once,
  // before the form is used; a refusal clears the dead cookie and leaves the form as it was.
  // The vault key is not re-derived — there is no password here to derive it from — so a
  // vault left locked is the case the sign-in below already allows for: the account panel
  // can recover it.
  async function resume() {
    busy(true);
    if (submitLabel) submitLabel.textContent = 'resuming…';
    try {
      const reply = await post('/auth/resume', {});
      if (reply.ok) { window.location.replace(destination()); return; }
    } catch (err) { /* fall through to the form */ }
    busy(false);
  }
  if (form.hasAttribute('data-resume')) resume();

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
      const { salt, B, id, kdf } = await challenge.json();
      const proof = await client.respond(salt, B, kdf);
      const verify = await post('/auth/verify',
                                { email: client.email, A: proof.A, M1: proof.M1, id, remember });
      if (!verify.ok) return fail('Sign-in failed. Check your email and password.');
      const { M2 } = await verify.json();
      if (!proof.check(M2)) return fail('Server failed mutual authentication — not signing in.');
      // Vault: derive PK from the password we still hold and the SRP
      // salt, for the per-user service to unlock the vault with. Best-effort — a
      // failure only means the vault stays locked (the account panel can recover).
      try {
        if (window.Vault) Vault.store(await Vault.derivePk(secret, salt), salt);
      } catch (err) { /* vault stays locked */ }
      window.location.replace(destination());
    } catch (err) {
      fail('Sign-in failed: ' + (err && err.message ? err.message : 'unexpected error'));
    }
  });
})();
