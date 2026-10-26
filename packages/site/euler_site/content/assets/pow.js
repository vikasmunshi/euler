/* Proof of work for the forms that make the service send mail (/forgot,
 * /request-invite) — the browser half of euler_site/auth/pow.py.
 *
 * A form marked [data-pow-bits] carries the server's signed stamp in its `pow`
 * field. On submit we search for a nonce such that SHA-256("<stamp>:<nonce>")
 * starts with that many zero bits, put it in `pow_nonce`, and submit for real.
 * About a second for a person; the point is that a script pays it per request.
 *
 * SHA-256 is computed here, synchronously, rather than with crypto.subtle: the
 * search is hundreds of thousands of tiny digests, and a promise per digest made
 * WebCrypto some fifty times slower than this loop. */
'use strict';

(() => {
  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]);
  const W = new Uint32Array(64);

  //: The first word of SHA-256(bytes) — all the zero-bit test needs (bits ≤ 32).
  function sha256FirstWord(bytes) {
    const blocks = ((bytes.length + 9 + 63) >> 6) << 6;
    const msg = new Uint8Array(blocks);
    msg.set(bytes);
    msg[bytes.length] = 0x80;
    const bitLength = bytes.length * 8;
    msg[blocks - 4] = bitLength >>> 24; msg[blocks - 3] = bitLength >>> 16;
    msg[blocks - 2] = bitLength >>> 8;  msg[blocks - 1] = bitLength;
    let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
    let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
    for (let off = 0; off < blocks; off += 64) {
      for (let i = 0; i < 16; i++) {
        const j = off + i * 4;
        W[i] = (msg[j] << 24) | (msg[j + 1] << 16) | (msg[j + 2] << 8) | msg[j + 3];
      }
      for (let i = 16; i < 64; i++) {
        const a = W[i - 15], b = W[i - 2];
        const s0 = ((a >>> 7) | (a << 25)) ^ ((a >>> 18) | (a << 14)) ^ (a >>> 3);
        const s1 = ((b >>> 17) | (b << 15)) ^ ((b >>> 19) | (b << 13)) ^ (b >>> 10);
        W[i] = W[i - 16] + s0 + W[i - 7] + s1;
      }
      let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
      for (let i = 0; i < 64; i++) {
        const S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        const t1 = (h + S1 + ((e & f) ^ (~e & g)) + K[i] + W[i]) | 0;
        const S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        const t2 = (S0 + ((a & b) ^ (a & c) ^ (b & c))) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      h0 = (h0 + a) | 0; h1 = (h1 + b) | 0; h2 = (h2 + c) | 0; h3 = (h3 + d) | 0;
      h4 = (h4 + e) | 0; h5 = (h5 + f) | 0; h6 = (h6 + g) | 0; h7 = (h7 + h) | 0;
    }
    return h0 >>> 0;
  }

  //: Search for the nonce, handing the page back its thread every few thousand tries.
  async function solve(stamp, bits) {
    const encoder = new TextEncoder();
    const limit = 2 ** (32 - bits);           // first word below this ⇔ `bits` zero bits
    for (let nonce = 0; ; ) {
      for (const end = nonce + 20000; nonce < end; nonce++) {
        if (sha256FirstWord(encoder.encode(stamp + ':' + nonce)) < limit) return String(nonce);
      }
      await new Promise((resume) => setTimeout(resume, 0));
    }
  }

  document.querySelectorAll('form[data-pow-bits]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const label = button ? button.textContent : '';
      if (button) { button.disabled = true; button.textContent = 'checking…'; }
      try {
        form.elements.pow_nonce.value = await solve(form.elements.pow.value,
                                                    Number(form.dataset.powBits));
        form.submit();                        // a programmatic submit does not re-enter here
      } catch (err) {
        if (button) { button.disabled = false; button.textContent = label; }
      }
    });
  });
})();
