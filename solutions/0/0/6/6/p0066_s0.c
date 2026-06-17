/* Solution to Euler Problem 66: Diophantine Equation. */
#include "runner.h"
#include <math.h>

/*
 * Pell's equation x^2 - D*y^2 = 1: the fundamental solution is found among the
 * continued-fraction convergents of sqrt(D), with the period parity selecting
 * the convergent index. O(D * sqrt(D)) big-integer operations for D up to max_d.
 */

/* Big integer: array of digits in base 10^9, little-endian */
#define BASE 1000000000ULL
#define MAX_LIMBS 512

typedef struct {
    unsigned long long d[MAX_LIMBS];
    int len;
} BigInt;

/* Set a BigInt to zero (length 1, single zero limb). */
static void bi_zero(BigInt *a) {
    memset(a->d, 0, sizeof(a->d));
    a->len = 1;
}

/* Initialise a BigInt from a 64-bit value, spilling into a second limb if needed. */
static void bi_set(BigInt *a, unsigned long long v) {
    bi_zero(a);
    a->d[0] = v % BASE;
    if (v >= BASE) {
        a->d[1] = v / BASE;
        a->len = 2;
    } else {
        a->len = 1;
    }
}

/* Copy b into a, limbs and length. */
static void bi_copy(BigInt *a, const BigInt *b) {
    memcpy(a->d, b->d, (size_t)b->len * sizeof(unsigned long long));
    a->len = b->len;
}

/* Compare two BigInts, returning -1, 0, or 1. */
static int bi_cmp(const BigInt *a, const BigInt *b) {
    if (a->len != b->len) return a->len < b->len ? -1 : 1;
    for (int i = a->len - 1; i >= 0; i--) {
        if (a->d[i] != b->d[i]) return a->d[i] < b->d[i] ? -1 : 1;
    }
    return 0;
}

/* Schoolbook addition result = a + b with carry propagation in base 10^9. */
static void bi_add(BigInt *result, const BigInt *a, const BigInt *b) {
    int maxlen = a->len > b->len ? a->len : b->len;
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < maxlen || carry; i++) {
        unsigned long long sum = carry;
        if (i < a->len) sum += a->d[i];
        if (i < b->len) sum += b->d[i];
        result->d[i] = sum % BASE;
        carry = sum / BASE;
    }
    result->len = i;
    while (result->len > 1 && result->d[result->len-1] == 0) result->len--;
}

/* Multiply a BigInt by a small scalar; the 128-bit product avoids limb overflow. */
static void bi_mul_small(BigInt *result, const BigInt *a, unsigned long long small) {
    if (small == 0) { bi_zero(result); return; }
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < a->len || carry; i++) {
        unsigned __int128 prod = carry;
        if (i < a->len) prod += (unsigned __int128)a->d[i] * small;
        result->d[i] = (unsigned long long)(prod % BASE);
        carry = (unsigned long long)(prod / BASE);
    }
    result->len = i;
    while (result->len > 1 && result->d[result->len-1] == 0) result->len--;
}

/* Generate one full period of the continued fraction of sqrt(D); stops at term 2*a0. */
static void compute_cf(int d, int *cf, int *cf_len) {
    int a0 = (int)floor(sqrt((double)d));
    cf[0] = a0;
    *cf_len = 1;
    int m = 0, n = 1, a = a0;
    while (a != 2 * a0) {
        m = n * a - m;
        n = (d - m * m) / n;
        a = (int)floor((sqrt((double)d) + m) / n);
        cf[(*cf_len)++] = a;
    }
}

/* Evaluate the n-th convergent backward (innermost term first), cycling the periodic part. */
static void compute_nth_convergent(int *cf, int cf_len, int n, BigInt *num_out, BigInt *den_out) {
    int period_length = cf_len - 1;

    int idx = (n - 1) % period_length + 1;
    BigInt num, den;
    bi_set(&num, (unsigned long long)cf[idx]);
    bi_set(&den, 1ULL);

    for (int i = n - 1; i >= 1; i--) {
        int tidx = (i - 1) % period_length + 1;
        int term = cf[tidx];
        BigInt new_num, tmp;
        bi_mul_small(&tmp, &num, (unsigned long long)term);
        bi_add(&new_num, &tmp, &den);
        bi_copy(&den, &num);
        bi_copy(&num, &new_num);
    }

    {
        BigInt tmp, new_num;
        bi_mul_small(&tmp, &num, (unsigned long long)cf[0]);
        bi_add(&new_num, &tmp, &den);
        bi_copy(den_out, &num);
        bi_copy(num_out, &new_num);
    }
}

/* Fundamental x for D: convergent index 2*L-3 if period L is even, else L-2 (perfect squares give 1). */
static void find_fundamental_x(int d, BigInt *best_x) {
    double sq = sqrt((double)d);
    if (sq == floor(sq)) {
        bi_set(best_x, 1ULL);
        return;
    }

    int cf[4096];
    int cf_len;
    compute_cf(d, cf, &cf_len);

    int n;
    if (cf_len % 2 == 0) {
        n = 2 * cf_len - 3;
    } else {
        n = cf_len - 2;
    }

    BigInt den;
    compute_nth_convergent(cf, cf_len, n, best_x, &den);
}

/*
 * Scan non-square D in [2, max_d], take the fundamental Pell x from continued-fraction
 * convergents of sqrt(D), and report the D maximising x. O(max_d * sqrt(max_d)) big-int ops.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_d = parse_int(argv[1]);

    int best_d = -1;
    BigInt best_x;
    bi_zero(&best_x);

    for (int d = 2; d <= max_d; d++) {
        double sq = sqrt((double)d);
        if (sq == floor(sq)) continue;

        BigInt x;
        find_fundamental_x(d, &x);

        if (bi_cmp(&x, &best_x) > 0) {
            bi_copy(&best_x, &x);
            best_d = d;
        }
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)best_d)); return _answer; }
}