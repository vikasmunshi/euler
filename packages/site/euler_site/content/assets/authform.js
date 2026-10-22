/* Shared sign-in / set-password affordances: password reveal toggles and the
 * caps-lock warning. The SRP handshakes live in login.js and register.js — this
 * is only chrome, wired the same way on every auth window that has a password. */
'use strict';

(() => {
  // Reveal toggles: each [data-pw-toggle] flips the field named by aria-controls
  // between password and text, and says which state it is in.
  document.querySelectorAll('[data-pw-toggle]').forEach((btn) => {
    const field = document.getElementById(btn.getAttribute('aria-controls'));
    if (!field) return;
    btn.addEventListener('click', () => {
      const reveal = field.type === 'password';
      field.type = reveal ? 'text' : 'password';
      btn.textContent = reveal ? 'hide' : 'show';
      btn.setAttribute('aria-pressed', reveal ? 'true' : 'false');
      field.focus();
    });
  });

  // Caps-lock warning — shown only while one of the credential fields holds
  // focus and Caps Lock is on. The listeners sit on the document, not the
  // fields: pressing the Caps Lock key to turn it *off* fires no reliable event
  // on the focused input, so a field-only listener leaves the warning stuck on.
  // A document keyup catches the toggle wherever the caret is; blur clears it
  // when focus leaves the fields entirely.
  const warn = document.getElementById('caps-warn');
  if (!warn) return;
  const fields = Array.from(
    document.querySelectorAll('input[type="password"], input[type="email"]'));
  if (!fields.length) return;
  const update = (event) => {
    if (typeof event.getModifierState !== 'function') return;
    const focused = fields.indexOf(document.activeElement) !== -1;
    warn.hidden = !(focused && event.getModifierState('CapsLock'));
  };
  document.addEventListener('keydown', update);
  document.addEventListener('keyup', update);
  fields.forEach((el) => el.addEventListener('blur', () => { warn.hidden = true; }));
})();
