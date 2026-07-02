// register.js — drive the two-step invite registration (verify OTP → set password).
import { srpVerifyOtp, srpRegister } from '/srp-client.js';

const MIN_PASSWORD_LENGTH = 12;  // mirrors solver.web.auth.policy.MIN_PASSWORD_LENGTH

const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const done = document.getElementById('done');
const errorBox = document.getElementById('error');

const emailInput = document.getElementById('email');
const otpInput = document.getElementById('otp');
const verifyButton = document.getElementById('verify');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm');
const createButton = document.getElementById('create');

let verifiedEmail = null;
let verifiedOtp = null;

// Prefill the email from the link in the OTP email (/register?email=…).
const prefillEmail = new URLSearchParams(location.search).get('email');
if (prefillEmail) {
    emailInput.value = prefillEmail;
    otpInput.focus();
}

document.getElementById('verify-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.textContent = '';
    verifyButton.disabled = true;
    try {
        const email = emailInput.value;
        const otp = otpInput.value.trim();
        const { ok } = await srpVerifyOtp(email, otp);
        if (ok) {
            verifiedEmail = email;
            verifiedOtp = otp;
            step1.classList.add('hidden');
            step2.classList.remove('hidden');
            passwordInput.focus();
        } else {
            errorBox.textContent = 'Invalid or expired code.';
        }
    } catch (err) {
        errorBox.textContent = 'Verification failed — please try again.';
    } finally {
        verifyButton.disabled = false;
    }
});

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
    createButton.disabled = true;
    try {
        const { ok } = await srpRegister(verifiedEmail, verifiedOtp, passwordInput.value);
        if (ok) {
            step2.classList.add('hidden');
            done.classList.remove('hidden');
        } else {
            errorBox.textContent = 'Registration failed — the code may have expired.';
        }
    } catch (err) {
        errorBox.textContent = 'Registration failed — please try again.';
    } finally {
        createButton.disabled = false;
    }
});
