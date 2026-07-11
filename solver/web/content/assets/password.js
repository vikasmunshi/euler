/* Change-password page (signed-in): prove the CURRENT password over SRP, then
 * submit the {salt, verifier} derived from the NEW one — neither password
 * leaves the browser. Distinct from the forgot/reset flow (no mailbox trip). */
'use strict';

(() => {
  const form = document.getElementById('password-form');
  if (!form) return;
  const errorBox = document.getElementById('form-error');
  const submit = document.getElementById('submit-btn');
  const MIN_LENGTH = 16;   // keep in sync with solver/web/auth/policy.py

  function fail(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    submit.disabled = false;
  }

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

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    submit.disabled = true;
    const current = document.getElementById('current').value;
    const next = document.getElementById('new1').value;
    const again = document.getElementById('new2').value;
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
      const { salt, B } = await challenge.json();
      const proof = await client.respond(salt, B);
      // 2 · derive the new credentials and swap them in one atomic exchange
      const derived = await SRP.computeVerifier(email, next);
      const change = await post('/auth/password', {
        A: proof.A, M1: proof.M1, salt: derived.salt, verifier: derived.verifier,
      });
      if (change.status === 401) return fail('The current password is incorrect.');
      if (!change.ok) return fail('The change was refused. Try again.');
      const { M2 } = await change.json();
      if (!proof.check(M2)) return fail('Server failed mutual authentication — password unchanged? Sign in to verify.');
      window.location.replace('/');
    } catch (err) {
      fail('Change failed: ' + (err && err.message ? err.message : 'unexpected error'));
    }
  });
})();
