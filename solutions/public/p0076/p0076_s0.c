/* Solution to Euler Problem 76: Counting Summations. */
#include "runner.h"

/* Big integer using base 10^9 limbs, little-endian */
#define BASE 1000000000LL
#define MAX_LIMBS 16

typedef struct {
    long long limbs[MAX_LIMBS];
    int n; /* number of limbs used */
} BigInt;

/* Set a big integer to a small non-negative value. */
static void bigint_set(BigInt *a, long long val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->n = 0;
    if (val == 0) { a->n = 1; return; }
    while (val > 0) {
        a->limbs[a->n++] = val % BASE;
        val /= BASE;
    }
}

/* result = a + b with carry propagation; base 10^9 keeps limb sums below 2^63. */
static void bigint_add(BigInt *result, const BigInt *a, const BigInt *b) {
    long long carry = 0;
    int maxn = (a->n > b->n) ? a->n : b->n;
    result->n = 0;
    for (int i = 0; i < maxn || carry; i++) {
        long long sum = carry;
        if (i < a->n) sum += a->limbs[i];
        if (i < b->n) sum += b->limbs[i];
        result->limbs[i] = sum % BASE;
        carry = sum / BASE;
        result->n = i + 1;
    }
}

/* result = a - b with borrow propagation; assumes a >= b. */
static void bigint_sub(BigInt *result, const BigInt *a, const BigInt *b) {
    /* a >= b assumed */
    long long borrow = 0;
    result->n = a->n;
    for (int i = 0; i < a->n; i++) {
        long long diff = a->limbs[i] - borrow - (i < b->n ? b->limbs[i] : 0);
        if (diff < 0) { diff += BASE; borrow = 1; }
        else borrow = 0;
        result->limbs[i] = diff;
    }
    while (result->n > 1 && result->limbs[result->n - 1] == 0) result->n--;
}

/* True when the big integer equals zero. */
static int bigint_is_zero(const BigInt *a) {
    return a->n == 1 && a->limbs[0] == 0;
}

/* Print a big integer: top limb plain, lower limbs zero-padded to 9 digits. */
static void bigint_print(const BigInt *a) {
    printf("%lld", a->limbs[a->n - 1]);
    for (int i = a->n - 2; i >= 0; i--) {
        printf("%09lld", a->limbs[i]);
    }
}

/* Generalized pentagonal number g(k) = k*(3k-1)/2 for any integer k. */
static long long pentagonal(int k) {
    return (long long)k * (3 * k - 1) / 2;
}

/*
 * Euler's pentagonal number theorem: fill p[0..num] bottom-up, then return p[num]-1.
 * Each p[n] is an alternating sum over generalized pentagonal offsets, so only about
 * sqrt(2n/3) earlier values are touched; overall O(n*sqrt(n)) with big-integer add/sub.
 */
const char *solve(int argc, char *argv[]) {
    int num = (argc > 1) ? parse_int(argv[1]) : 100;

    /* p[i] = number of partitions of i */
    BigInt *p = calloc((size_t)(num + 1), sizeof(BigInt));
    if (!p) { fprintf(stderr, "out of memory\n"); return NULL; }

    bigint_set(&p[0], 1);

    for (int n = 1; n <= num; n++) {
        bigint_set(&p[n], 0);
        for (int k = 1; ; k++) {
            long long g_pos = pentagonal(k);
            long long g_neg = pentagonal(-k);
            int done_pos = (g_pos > n);
            int done_neg = (g_neg > n);

            BigInt tmp, tmp2;
            bigint_set(&tmp, 0);
            bigint_set(&tmp2, 0);

            if (!done_pos) bigint_add(&tmp, &tmp, &p[n - (int)g_pos]);
            if (!done_neg) bigint_add(&tmp2, &tmp2, &p[n - (int)g_neg]);

            /* combined = tmp + tmp2 */
            BigInt combined;
            bigint_add(&combined, &tmp, &tmp2);

            if (k % 2 == 1) {
                /* add combined to p[n] */
                BigInt res;
                bigint_add(&res, &p[n], &combined);
                p[n] = res;
            } else {
                /* subtract combined from p[n] */
                BigInt res;
                bigint_sub(&res, &p[n], &combined);
                p[n] = res;
            }

            /* g(k) grows like 3k^2/2, so both offsets exceed n after ~sqrt(2n/3) steps. */
            if (done_pos && done_neg) break;
        }
    }

    /* answer = p[num] - 1 */
    BigInt one, answer;
    bigint_set(&one, 1);
    bigint_sub(&answer, &p[num], &one);

    /* Format answer as string */
    /* Compute length needed */
    int len = 0;
    char *buf = malloc(MAX_LIMBS * 10 + 2);
    if (!buf) { free(p); return NULL; }
    char tmp_buf[32];
    len = snprintf(tmp_buf, sizeof(tmp_buf), "%lld", answer.limbs[answer.n - 1]);
    strcpy(buf, tmp_buf);
    for (int i = answer.n - 2; i >= 0; i--) {
        char seg[16];
        snprintf(seg, sizeof(seg), "%09lld", answer.limbs[i]);
        strcat(buf, seg);
    }

    free(p);
    return buf;
}