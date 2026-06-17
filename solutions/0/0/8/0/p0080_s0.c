/* Solution to Euler Problem 80: Square Root Digital Expansion. */
#include "runner.h"
#include <math.h>

/*
 * Arbitrary-precision integer arithmetic.
 * Base B = 10^9, little-endian limbs.
 * Numbers up to ~200 decimal digits => ~23 limbs. MAXLIMBS=64 for safety.
 */
#define BASE     1000000000ULL
#define MAXLIMBS 64

typedef unsigned long long ull;
typedef __uint128_t u128;

typedef struct { ull limbs[MAXLIMBS]; int size; } BigInt;

/* Set a to zero (canonical one-limb form). */
static void bi_zero(BigInt *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->size = 1;
}

/* Initialize a from a 64-bit value, splitting into at most two base-10^9 limbs. */
static void bi_from_ull(BigInt *a, ull v) {
    bi_zero(a);
    a->limbs[0] = v % BASE;
    if (v >= BASE) { a->limbs[1] = v / BASE; a->size = 2; }
}

/* Copy src into dst. */
static void bi_copy(BigInt *dst, const BigInt *src) {
    memcpy(dst, src, sizeof(BigInt));
}

/* Drop leading zero limbs, keeping at least one. */
static void bi_trim(BigInt *a) {
    while (a->size > 1 && a->limbs[a->size-1] == 0) a->size--;
}

/* Compare magnitudes: returns -1, 0, or 1 for a < b, a == b, a > b. */
static int bi_cmp(const BigInt *a, const BigInt *b) {
    if (a->size != b->size) return a->size > b->size ? 1 : -1;
    for (int i = a->size-1; i >= 0; i--) {
        if (a->limbs[i] > b->limbs[i]) return  1;
        if (a->limbs[i] < b->limbs[i]) return -1;
    }
    return 0;
}

/* dst = a + b with carry propagation across limbs. */
static void bi_add(BigInt *dst, const BigInt *a, const BigInt *b) {
    int n = a->size > b->size ? a->size : b->size;
    ull carry = 0;
    for (int i = 0; i < n || carry; i++) {
        ull s = carry + (i < a->size ? a->limbs[i] : 0)
                      + (i < b->size ? b->limbs[i] : 0);
        if (i < MAXLIMBS) dst->limbs[i] = s % BASE;
        carry = s / BASE;
        if (i >= n) n++;
    }
    dst->size = n < MAXLIMBS ? n : MAXLIMBS;
    bi_trim(dst);
}

/* dst = a - b assuming a >= b, with borrow propagation. */
static void bi_sub(BigInt *dst, const BigInt *a, const BigInt *b) {
    long long borrow = 0;
    int n = a->size;
    for (int i = 0; i < n; i++) {
        long long d = (long long)a->limbs[i]
                    - (i < b->size ? (long long)b->limbs[i] : 0LL) - borrow;
        if (d < 0) { d += (long long)BASE; borrow = 1; } else borrow = 0;
        dst->limbs[i] = (ull)d;
    }
    dst->size = n;
    bi_trim(dst);
}

/* dst = a / 2, propagating the odd-limb remainder downward as carry. */
static void bi_div2(BigInt *dst, const BigInt *a) {
    bi_copy(dst, a);
    ull carry = 0;
    for (int i = dst->size-1; i >= 0; i--) {
        ull cur = dst->limbs[i] + carry * BASE;
        dst->limbs[i] = cur / 2;
        carry = cur & 1ULL;
    }
    bi_trim(dst);
}

/* dst = a * b via schoolbook O(size_a * size_b); products fit in u128 per limb pair. */
static void bi_mul(BigInt *dst, const BigInt *a, const BigInt *b) {
    BigInt t;
    memset(&t, 0, sizeof(t));
    t.size = (a->size + b->size < MAXLIMBS) ? a->size + b->size : MAXLIMBS;
    for (int i = 0; i < a->size; i++) {
        ull carry = 0;
        for (int j = 0; j < b->size && i+j < MAXLIMBS; j++) {
            ull cur = t.limbs[i+j] + a->limbs[i] * b->limbs[j] + carry;
            t.limbs[i+j] = cur % BASE;
            carry = cur / BASE;
        }
        if (i + b->size < MAXLIMBS) t.limbs[i + b->size] += carry;
    }
    bi_trim(&t);
    bi_copy(dst, &t);
}

/* dst = a * v for a single-limb multiplier v. */
static void bi_mul_limb(BigInt *dst, const BigInt *a, ull v) {
    ull carry = 0;
    int n = a->size;
    for (int i = 0; i < n; i++) {
        ull cur = a->limbs[i] * v + carry;
        dst->limbs[i] = cur % BASE;
        carry = cur / BASE;
    }
    if (carry && n < MAXLIMBS) { dst->limbs[n] = carry; n++; }
    dst->size = n;
    bi_trim(dst);
}

/* a = 10^exp, built by repeated single-limb multiplies (chunks of 9 plus remainder). */
static void bi_pow10(BigInt *a, int exp) {
    bi_from_ull(a, 1);
    BigInt t;
    ull base9 = 1000000000ULL;
    int chunks = exp / 9, rem = exp % 9;
    ull baserem = 1;
    for (int i = 0; i < rem; i++) baserem *= 10;
    for (int i = 0; i < chunks; i++) { bi_mul_limb(&t, a, base9); bi_copy(a, &t); }
    if (baserem > 1) { bi_mul_limb(&t, a, baserem); bi_copy(a, &t); }
}

/* q = floor(a / b) by Knuth Algorithm D: normalize, estimate each quotient digit, correct. */
static void bi_div(BigInt *q, const BigInt *a, const BigInt *b) {
    if (bi_cmp(a, b) < 0) { bi_from_ull(q, 0); return; }

    if (b->size == 1) {
        ull carry = 0;
        BigInt qq;
        qq.size = a->size;
        memset(qq.limbs, 0, sizeof(qq.limbs));
        for (int i = a->size-1; i >= 0; i--) {
            ull cur = carry * BASE + a->limbs[i];
            qq.limbs[i] = cur / b->limbs[0];
            carry = cur % b->limbs[0];
        }
        bi_trim(&qq);
        bi_copy(q, &qq);
        return;
    }

    int n = b->size;
    int m = a->size - n;

    /* Normalize so the top divisor limb is >= BASE/2, tightening the q_hat estimate. */
    ull d = BASE / (b->limbs[n-1] + 1);

    BigInt u, v;
    bi_mul_limb(&u, a, d);
    bi_mul_limb(&v, b, d);

    /* Ensure u has at least m+n+1 limbs */
    while (u.size < m + n + 1 && u.size < MAXLIMBS) u.limbs[u.size++] = 0;

    BigInt qq;
    bi_zero(&qq);
    qq.size = m + 1;

    for (int j = m; j >= 0; j--) {
        ull uj_n  = (j+n   < MAXLIMBS) ? u.limbs[j+n]   : 0;
        ull uj_n1 = (j+n-1 >= 0 && j+n-1 < MAXLIMBS) ? u.limbs[j+n-1] : 0;
        ull uj_n2 = (j+n-2 >= 0 && j+n-2 < MAXLIMBS) ? u.limbs[j+n-2] : 0;
        ull vn1 = v.limbs[n-1];
        ull vn2 = (n >= 2) ? v.limbs[n-2] : 0;

        /* Estimate quotient digit from the top two dividend limbs; u128 avoids overflow. */
        u128 top2 = (u128)uj_n * BASE + uj_n1;
        ull q_hat = (ull)(top2 / vn1);
        if (q_hat >= BASE) q_hat = BASE - 1;

        /* Refinement */
        for (int iter = 0; iter < 2; iter++) {
            u128 rem = top2 - (u128)q_hat * vn1;
            if (rem >= BASE) break;
            if ((u128)q_hat * vn2 > rem * BASE + uj_n2) q_hat--;
            else break;
        }

        /* u[j..j+n] -= q_hat * v */
        long long borrow = 0;
        ull carry = 0;
        for (int i = 0; i <= n; i++) {
            ull vi = (i < n) ? v.limbs[i] : 0;
            ull prod = vi * q_hat + carry;
            carry = prod / BASE;
            prod %= BASE;
            int idx = j + i;
            long long diff = (idx < MAXLIMBS ? (long long)u.limbs[idx] : 0)
                           - (long long)prod - borrow;
            if (diff < 0) { diff += (long long)BASE; borrow = 1; } else borrow = 0;
            if (idx < MAXLIMBS) u.limbs[idx] = (ull)diff;
        }

        if (borrow) {
            /* q_hat overshot by one: decrement and add v back into u[j..j+n]. */
            q_hat--;
            ull carry2 = 0;
            for (int i = 0; i <= n; i++) {
                int idx = j + i;
                ull vi = (i < n) ? v.limbs[i] : 0;
                ull s = (idx < MAXLIMBS ? u.limbs[idx] : 0) + vi + carry2;
                if (idx < MAXLIMBS) u.limbs[idx] = s % BASE;
                carry2 = s / BASE;
            }
        }

        qq.limbs[j] = q_hat;
    }

    bi_trim(&qq);
    bi_copy(q, &qq);
}

/* Convert to decimal string; caller frees. Top limb plain, rest zero-padded to 9 digits. */
static char *bi_to_str(const BigInt *a) {
    char *buf = malloc((size_t)(a->size * 9 + 4));
    if (!buf) return NULL;
    int pos = sprintf(buf, "%llu", a->limbs[a->size-1]);
    for (int i = a->size-2; i >= 0; i--)
        pos += sprintf(buf + pos, "%09llu", a->limbs[i]);
    return buf;
}

/* O(1) test: round sqrt(n) to a double and check the nearby integers exactly. */
static int is_perfect_square(int n) {
    int s = (int)(sqrt((double)n) + 0.5);
    for (int k = s-1; k <= s+1; k++)
        if (k > 0 && k * k == n) return 1;
    return 0;
}

/*
 * Sum the first `digits` decimal digits of sqrt(n) via floor(sqrt(n * 10^(2*digits)))
 * computed by Heron's (Newton's) method. Quadratic convergence: ~7 iterations for 100 digits.
 */
static int sqrt_digit_sum_heron(int n, int digits) {
    BigInt scale;
    bi_pow10(&scale, 2 * digits);

    BigInt scaled;
    bi_from_ull(&scaled, (ull)n);
    { BigInt t; bi_mul(&t, &scaled, &scale); bi_copy(&scaled, &t); }

    /*
     * Initial guess: slightly above sqrt(n)*10^digits.
     * Use double to get ~15 significant digits, add margin, then scale by 10^(digits-15).
     * Seeding above the true root keeps the iterates monotone-decreasing to the floor.
     */
    BigInt x;
    {
        double approx = sqrt((double)n) * 1e15 + 100.0;
        bi_from_ull(&x, (ull)approx);
        BigInt es;
        bi_pow10(&es, digits - 15);
        BigInt t;
        bi_mul(&t, &x, &es);
        bi_copy(&x, &t);
    }

    /* Heron iteration: x = (x + scaled/x) / 2 until x_new >= x */
    BigInt q, s, xnew;
    for (;;) {
        bi_div(&q, &scaled, &x);
        bi_add(&s, &x, &q);
        bi_div2(&xnew, &s);
        if (bi_cmp(&xnew, &x) >= 0) break;
        bi_copy(&x, &xnew);
    }

    char *str = bi_to_str(&x);
    if (!str) return 0;
    int sum = 0;
    int len = (int)strlen(str);
    int take = len < digits ? len : digits;
    for (int i = 0; i < take; i++) sum += str[i] - '0';
    free(str);
    return sum;
}

/*
 * Sum digit sums of the first `digits` decimals of every irrational sqrt(n) for n in [2, max_num].
 * Each root uses Heron integer sqrt of the 10^(2*digits)-scaled value; O(N * d^2) overall.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int digits  = parse_int(argv[1]);
    int max_num = parse_int(argv[2]);
    long long result = 0;
    for (int i = 2; i <= max_num; i++) {
        if (is_perfect_square(i)) continue;
        result += sqrt_digit_sum_heron(i, digits);
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}