// login.js — drive the SRP-6a login form.
import { srpLogin } from '/srp-client.js';

const form = document.getElementById('login-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const rememberInput = document.getElementById('remember');
const submitButton = document.getElementById('submit');
const errorBox = document.getElementById('error');

function safeNext() {
    const next = new URLSearchParams(location.search).get('next') || '/';
    return (next.startsWith('/') && !next.startsWith('//')) ? next : '/';
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.textContent = '';
    submitButton.disabled = true;
    try {
        const { ok } = await srpLogin(emailInput.value, passwordInput.value, rememberInput.checked);
        if (ok) {
            location.assign(safeNext());
        } else {
            errorBox.textContent = 'Incorrect email or password.';
            passwordInput.value = '';
            passwordInput.focus();
        }
    } catch (err) {
        errorBox.textContent = 'Login failed — please try again.';
    } finally {
        submitButton.disabled = false;
    }
});
