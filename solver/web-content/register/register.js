// register.js — validate the emailed secure link, then set the password.
import { srpValidateToken, srpRegister, validatePassword, generatePassword } from '/srp-client.js';

const checking = document.getElementById('checking');
const invalid = document.getElementById('invalid');
const stepPassword = document.getElementById('step-password');
const done = document.getElementById('done');
const errorBox = document.getElementById('error');

const accountInput = document.getElementById('account');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm');
const createButton = document.getElementById('create');

const token = new URLSearchParams(location.search).get('token') || '';
let accountEmail = null;

wireGenerator(passwordInput, confirmInput);

// On load: the page is reachable only through the emailed link, so validate the
// token up front and show the target email (or an "invalid link" message).
(async () => {
    if (!token) {
        checking.classList.add('hidden');
        invalid.classList.remove('hidden');
        return;
    }
    try {
        const { ok, email } = await srpValidateToken(token);
        checking.classList.add('hidden');
        if (ok) {
            accountEmail = email;
            accountInput.value = email;
            stepPassword.classList.remove('hidden');
            passwordInput.focus();
        } else {
            invalid.classList.remove('hidden');
        }
    } catch (err) {
        checking.classList.add('hidden');
        invalid.classList.remove('hidden');
    }
})();

document.getElementById('password-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.textContent = '';
    const { ok: valid, message } = validatePassword(passwordInput.value);
    if (!valid) {
        errorBox.textContent = message;
        return;
    }
    if (passwordInput.value !== confirmInput.value) {
        errorBox.textContent = 'Passwords do not match.';
        return;
    }
    createButton.disabled = true;
    try {
        const { ok } = await srpRegister(token, accountEmail, passwordInput.value);
        if (ok) {
            stepPassword.classList.add('hidden');
            done.classList.remove('hidden');
        } else {
            errorBox.textContent = 'Registration failed — the link may have expired.';
        }
    } catch (err) {
        errorBox.textContent = 'Registration failed — please try again.';
    } finally {
        createButton.disabled = false;
    }
});

// Wire the "Generate / Copy / Use" password generator (same UI on the change-password
// page). `fields` are the inputs the "Use" button fills.
function wireGenerator(...fields) {
    const generate = document.getElementById('generate');
    const output = document.getElementById('generated');
    const copy = document.getElementById('copy');
    const use = document.getElementById('use');
    if (!generate || !output) return;

    generate.addEventListener('click', () => {
        output.value = generatePassword();
        copy.hidden = false;
        use.hidden = false;
    });
    copy.addEventListener('click', async () => {
        if (!output.value) return;
        try {
            await navigator.clipboard.writeText(output.value);
            copy.textContent = 'Copied';
            setTimeout(() => { copy.textContent = 'Copy'; }, 1500);
        } catch (err) {
            output.select();  // clipboard blocked → let the user copy manually
        }
    });
    use.addEventListener('click', () => {
        if (!output.value) return;
        for (const field of fields) field.value = output.value;
        fields[0].focus();
    });
}
