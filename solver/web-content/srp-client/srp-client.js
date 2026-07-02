// srp-client.js — browser SRP-6a login, byte-compatible with solver/web/auth/srp.py.
//
// The password never leaves the browser: we prove knowledge of it against the
// server's stored verifier via the SRP-6a challenge/response, then verify the
// server's proof (mutual auth) before trusting the session.
//
// Parameters MUST match srp.py exactly: RFC 5054 2048-bit group, g = 2, SHA-256,
// PAD to |N| = 256 bytes, x = H(salt | H(email ":" password)),
// M1 = H(H(N) XOR H(g) | H(email) | salt | PAD(A) | PAD(B) | K), M2 = H(PAD(A) | M1 | K).
// Run `SRP._selfTest()` in the browser console to check interop against the
// reference vectors baked into the Python test suite.

const N = BigInt('0x' +
    'AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050' +
    'A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50' +
    'E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B8' +
    '55F97993EC975EEAA80D740ADBF4FF747359D041D5C33EA71D281E446B14773B' +
    'CA97B43A23FB801676BD207A436C6481F1D2B9078717461A5B9D32E688F87748' +
    '544523B524B0D57D5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6' +
    'AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6' +
    '94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F9E4AFF73');
const g = 2n;
const N_BYTES = 256;

// --- byte / bigint helpers -------------------------------------------------
function mod(a, n) { return ((a % n) + n) % n; }

function modpow(base, exp, m) {
    base = mod(base, m);
    let result = 1n;
    while (exp > 0n) {
        if (exp & 1n) result = (result * base) % m;
        exp >>= 1n;
        base = (base * base) % m;
    }
    return result;
}

function concatBytes(arrays) {
    let len = 0;
    for (const a of arrays) len += a.length;
    const out = new Uint8Array(len);
    let off = 0;
    for (const a of arrays) { out.set(a, off); off += a.length; }
    return out;
}

function bytesToBigInt(bytes) {
    let x = 0n;
    for (const b of bytes) x = (x << 8n) | BigInt(b);
    return x;
}

function bigIntToBytes(x, len) {
    const out = new Uint8Array(len);      // zero-filled → left-padded
    let v = x;
    for (let i = len - 1; i >= 0 && v > 0n; i--) { out[i] = Number(v & 0xffn); v >>= 8n; }
    return out;
}

function pad(x) { return bigIntToBytes(x, N_BYTES); }

function utf8(s) { return new TextEncoder().encode(s); }

function bytesToHex(bytes) {
    return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
    const h = hex.length % 2 ? '0' + hex : hex;
    const out = new Uint8Array(h.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
    return out;
}

function xorBytes(a, b) {
    const out = new Uint8Array(a.length);
    for (let i = 0; i < a.length; i++) out[i] = a[i] ^ b[i];
    return out;
}

async function H(...arrays) {
    const digest = await crypto.subtle.digest('SHA-256', concatBytes(arrays));
    return new Uint8Array(digest);
}

async function Hint(...arrays) { return bytesToBigInt(await H(...arrays)); }

function randomExponent() {
    const bytes = new Uint8Array(32);
    crypto.getRandomValues(bytes);
    return 1n + mod(bytesToBigInt(bytes), N - 1n);
}

// Multiplier k = H(N | PAD(g)), computed once.
let _k = null;
async function multiplier() {
    if (_k === null) _k = await Hint(pad(N), pad(g));
    return _k;
}

async function deriveX(saltBytes, email, password) {
    const inner = await H(utf8(email + ':' + password));
    return Hint(saltBytes, inner);            // x = H(salt | H(email ":" password))
}

// Core client computation. `aOverride` is for the self-test only.
async function computeClient(email, password, saltBytes, B, aOverride) {
    const a = (aOverride !== undefined) ? aOverride : randomExponent();
    const A = modpow(g, a, N);
    const x = await deriveX(saltBytes, email, password);
    const u = await Hint(pad(A), pad(B));
    const k = await multiplier();
    const base = mod(B - k * modpow(g, x, N), N);
    const S = modpow(base, a + u * x, N);
    const K = await H(pad(S));
    const prefix = xorBytes(await H(pad(N)), await H(pad(g)));
    const M1 = await H(prefix, await H(utf8(email)), saltBytes, pad(A), pad(B), K);
    const M2 = await H(pad(A), M1, K);        // expected server proof (mutual auth)
    return { A, M1, K, M2 };
}

function normalizeEmail(email) { return email.trim().toLowerCase(); }

// --- public API ------------------------------------------------------------
// Perform an SRP-6a login. Resolves { ok: true } on success (server proof
// verified + session cookie set), { ok: false } otherwise.
export async function srpLogin(email, password) {
    const nemail = normalizeEmail(email);
    const challenge = await fetch('/auth/challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: nemail }),
    });
    if (!challenge.ok) return { ok: false };
    const { salt, B } = await challenge.json();

    const { A, M1, M2 } = await computeClient(nemail, password, hexToBytes(salt), BigInt('0x' + B));

    const verify = await fetch('/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: nemail, A: A.toString(16), M1: bytesToHex(M1) }),
    });
    if (!verify.ok) return { ok: false };
    const { M2: serverM2 } = await verify.json();
    return { ok: serverM2 === bytesToHex(M2) };   // reject a server that can't prove K
}

// Compute a fresh SRP salt + verifier for registration (v = g^x mod N).
export async function srpMakeVerifier(email, password) {
    const nemail = normalizeEmail(email);
    const salt = new Uint8Array(16);
    crypto.getRandomValues(salt);
    const x = await deriveX(salt, nemail, password);
    return { salt: bytesToHex(salt), verifier: modpow(g, x, N).toString(16) };
}

// Pre-check an OTP (does not consume it) — for immediate feedback on the register page.
export async function srpVerifyOtp(email, otp) {
    const response = await fetch('/register/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: normalizeEmail(email), otp }),
    });
    return { ok: response.ok };
}

// Complete registration: derive the verifier locally and submit it with the OTP.
export async function srpRegister(email, otp, password) {
    const nemail = normalizeEmail(email);
    const { salt, verifier } = await srpMakeVerifier(nemail, password);
    const response = await fetch('/register/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: nemail, otp, salt, verifier }),
    });
    return { ok: response.ok };
}

// Interop check against the reference vectors (see tests/test_srp.py).
export async function _selfTest() {
    const email = 'user@example.com';
    const password = 'correct horse battery staple';
    const salt = hexToBytes('00112233445566778899aabbccddeeff');
    const aExp = BigInt('0x' + 'deadbeef'.repeat(8));
    const B = BigInt('0x' +
        'f59f2d65fb89b5c26b2a83763f79670f25c2b7251f5e751ac5be6193e200f462' +
        '50ef66721c6be18755c4a27e1dc9f13dca8e1b76e2e394b5a51bcfdf65ea112f' +
        '9a3a22f3043b1dd69afc0efbb147393ec58141d33c92e0b2fa86c9f491792b65' +
        '9628a8a59fb174ae34a75a37ba107d2356582e01362a1cbc80a05308a8dc47cb' +
        '528724c19faa8df95c1d89102b85cfef8d5703d791034d951a9e22be2ee5a342' +
        '896fe908e6db5ab8930b2a9bae2f7de5b4016fe88a07ea0a0f4bdb937ca0b795' +
        '77e87c7cc83b861ec1cb8ff9927e90e654b590862b19a584e2dea2207f73e232' +
        '727814c66dc391107d6940726d31b8134f3ca7ac3c172abcf061e37301b370f');
    const expect = {
        A: '61e5a51ed7b9e8bf100c40e319cf6f6891f6ac7119fa1f5e959614a378e9fe1b' +
           'bd7071192ef0e8f2c22664e4547bfd7200cce038c66fd1b27ccbb9f87c098530' +
           '0466ef03b02b0e538a3bcdfb34f28fb8dcb2c9c96c22ba2547d5ab0669b39ebe' +
           'ac057285a98b6bd401f390b3b5f7d13ee71baa47bddd70d0a4f5069347e99f58' +
           'addaf7ca8888bc453fe8a7e041ffe7ca1f1cb74daaee1260ff004d424d3f5bdd' +
           'c1e235c3e792fb8d90bdd3f0f944b38e28f9a8cb6f50a3f6d99a7c58c60ffe86' +
           'e1f9a33c2ee10e40997b45f77b1bcc215fa1b560b0fb400c2df94d1b38aa997d' +
           '797dec940466ae9191f9ce8e34cf791a75a83161280d7f0b196c5bb0cfd3a37d',
        M1: '246d0effd76fb2c58b41fcf73c8b1bab1329ce6bca190efb639a21edf6e91df7',
        M2: '660f648df00840decddece5c403a6a80f50b801607212c109f7135a386393fb2',
        K: 'fbe681f3f72b005e752c66a5360d0965708074d1b0d602393622a0657f459e80',
    };
    const verifierHex =
        '412cadf21c82bd3c7659cfa6c9112ab5b25cb744b873fc6e7cb6df3088158525' +
        'f75b42c21285d7292b74ce7a51160b57ea635cac09242afcbc428df10e80111f' +
        'c791398d33dc630640fb2d020b16e50bb2dcb2d70c2f739a5800203e1e808eeb' +
        '594a3ed25d4fd0e7d0445f971e9740c7dc17c6a68b3c5047df2d74ffa4ba6823' +
        '6fee5e636ca19256b5af5d819e487750e52528efa880ec2cf46faa6730e79d1b' +
        '9ec9dce85166a83b380887bb0590847fe61ae5a666b4da6d08dc8f2a97fd7cbc' +
        '6c32651284adcee46e08acee4605e9e866b18af31536de4da47060fe0c2252cd' +
        'aa67a050cf839217a5ac79655afefb407d1c5be7595528f16af072aa20f1337e';

    const { A, M1, K, M2 } = await computeClient(email, password, salt, B, aExp);
    const verifier = modpow(g, await deriveX(salt, email, password), N).toString(16);
    const got = { A: A.toString(16), M1: bytesToHex(M1), M2: bytesToHex(M2), K: bytesToHex(K), verifier };
    const pass = got.A === expect.A && got.M1 === expect.M1 && got.M2 === expect.M2 &&
        got.K === expect.K && got.verifier === verifierHex;
    if (!pass) console.error('SRP self-test FAILED', { got, expect: { ...expect, verifier: verifierHex } });
    else console.log('SRP self-test passed — interop with srp.py confirmed');
    return pass;
}

export const SRP = { srpLogin, srpMakeVerifier, srpVerifyOtp, srpRegister, _selfTest };
if (typeof window !== 'undefined') window.SRP = SRP;
