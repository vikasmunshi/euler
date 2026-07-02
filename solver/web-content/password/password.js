// password.js — self-service password change for the signed-in user.
import { srpChangePassword } from '/srp-client.js';

const MIN_PASSWORD_LENGTH = 12;  // mirrors solver.web.auth.policy.MIN_PASSWORD_LENGTH

const formSection = document.getElementById('form-section');
const done = document.getElementById('done');
const errorBox = document.getElementById('error');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm');
const submitButton = document.getElementById('submit');

document.getElementById('password-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.textContent = '';
    if (passwordInput.value.length < MIN_PASSWORD_LENGTH) {
        errorBox.textContent = `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
        return;
    }
    if (passwordInput.value !== confirmInput.value) {
        errorBox.textContent = 'Passwords do not match.';
        return;
    }
    submitButton.disabled = true;
    try {
        const { ok } = await srpChangePassword(passwordInput.value);
        if (ok) {
            formSection.classList.add('hidden');
            done.classList.remove('hidden');
        } else {
            errorBox.textContent = 'Could not update password — please try again.';
        }
    } catch (err) {
        errorBox.textContent = 'Could not update password — please try again.';
    } finally {
        submitButton.disabled = false;
    }
});
