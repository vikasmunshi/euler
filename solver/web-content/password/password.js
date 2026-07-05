// password.js — self-service password change for the signed-in user.
import { srpChangePassword, validatePassword, generatePassword } from '/srp-client.js';

const formSection = document.getElementById('form-section');
const done = document.getElementById('done');
const errorBox = document.getElementById('error');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm');
const submitButton = document.getElementById('submit');

wireGenerator(passwordInput, confirmInput);

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

// Wire the "Generate / Copy / Use" password generator (same UI as the register page).
// `fields` are the inputs the "Use" button fills.
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
