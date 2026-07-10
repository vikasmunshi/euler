/* Sign-in page: drive the SRP-6a handshake against the auth service.
 * The password never leaves the browser; the server proves itself back (M2). */
'use strict';

(() => {
  const form = document.getElementById('login-form');
  if (!form) return;
  const errorBox = document.getElementById('form-error');
  const submit = document.getElementById('submit-btn');

  function fail(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    submit.disabled = false;
  }

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
    submit.disabled = true;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    try {
      const client = await SRP.startLogin(email, password);
      const challenge = await post('/auth/challenge', { email: client.email });
      if (!challenge.ok) return fail('Sign-in failed. Check your email and password.');
      const { salt, B } = await challenge.json();
      const proof = await client.respond(salt, B);
      const verify = await post('/auth/verify',
                                { email: client.email, A: proof.A, M1: proof.M1, remember });
      if (!verify.ok) return fail('Sign-in failed. Check your email and password.');
      const { M2 } = await verify.json();
      if (!proof.check(M2)) return fail('Server failed mutual authentication — not signing in.');
      window.location.replace('/');
    } catch (err) {
      fail('Sign-in failed: ' + (err && err.message ? err.message : 'unexpected error'));
    }
  });
})();
