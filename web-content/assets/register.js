/* Set-password stage (registration and reset): enforce the password policy,
 * derive the SRP {salt, verifier} in the browser, and submit only those —
 * the password itself never leaves this page (DD-7 step 5). */
'use strict';

(() => {
  const form = document.getElementById('password-form');
  if (!form) return;
  const errorBox = document.getElementById('form-error');
  const submit = document.getElementById('submit');
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

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    submit.disabled = true;
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm').value;
    if (password !== confirm) return fail('The passwords do not match.');
    const problem = policyError(password);
    if (problem) return fail(problem);
    try {
      const { salt, verifier } = await SRP.computeVerifier(form.dataset.email, password);
      form.elements.salt.value = salt;
      form.elements.verifier.value = verifier;
      document.getElementById('password').value = '';
      document.getElementById('confirm').value = '';
      form.submit();
    } catch (err) {
      fail('Could not derive the verifier: ' + (err && err.message ? err.message : 'unexpected error'));
    }
  });
})();
