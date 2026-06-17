/* Solution to Euler Problem 65: Convergents of $e$. */
#include "runner.h"

#define BASE 1000000000ULL
#define MAXDIGITS 2000

/* Arbitrary-precision unsigned integer: limbs in base 10^9 (a decimal base, so the digit sum
   is read off directly without any base conversion). */
typedef struct {
    unsigned long long d[MAXDIGITS];
    int len;
} BigInt;

/* Initialise a BigInt to a small unsigned value (at most two base-10^9 limbs). */
static void bigint_set(BigInt *a, unsigned long long val) {
    memset(a->d, 0, sizeof(a->d));
    a->len = 1;
    a->d[0] = val % BASE;
    if (val >= BASE) {
        a->d[1] = val / BASE;
        a->len = 2;
    }
}

/* dst = a * scalar + b, fused in one limb pass. With BASE = 10^9 and small scalar, the product
   av*scalar + bv + carry stays within 64 bits, so no per-limb overflow can occur. */
static void bigint_mul_add(BigInt *dst, const BigInt *a, unsigned long long scalar, const BigInt *b) {
    int maxlen = a->len > b->len ? a->len : b->len;
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < maxlen + 2; i++) {
        unsigned long long av = (i < a->len) ? a->d[i] : 0ULL;
        unsigned long long bv = (i < b->len) ? b->d[i] : 0ULL;
        unsigned long long val = av * scalar + bv + carry;
        dst->d[i] = val % BASE;
        carry = val / BASE;
    }
    dst->len = maxlen + 2;
    while (dst->len > 1 && dst->d[dst->len - 1] == 0)
        dst->len--;
}

/* Sum the decimal digits of a BigInt by decoding each limb with a mod-10 loop. */
static long long bigint_digit_sum(const BigInt *a) {
    long long sum = 0;
    for (int i = 0; i < a->len; i++) {
        unsigned long long v = a->d[i];
        while (v > 0) {
            sum += (long long)(v % 10);
            v /= 10;
        }
    }
    return sum;
}

/* Return the n-th partial quotient of e: 2 at n==1, 2*(n/3) when 3 | n, else 1. */
static int e_denominator(int n) {
    if (n == 1) return 2;
    if (n % 3 == 0) return 2 * (n / 3);
    return 1;
}

const char *solve(int argc, char *argv[]) {
    /* Iterate the convergent-numerator recurrence h(k) = a(k)*h(k-1) + h(k-2) with big integers,
       keeping a sliding window of the last two values, then sum the numerator's digits; ~O(n^2)
       digit-ops. Mirrors the Python sibling, but with a hand-rolled base-10^9 BigInt. */
    static char _answer[32];
    int n = parse_int(argv[1]);

    BigInt *h_prev2 = (BigInt *)malloc(sizeof(BigInt));
    BigInt *h_prev1 = (BigInt *)malloc(sizeof(BigInt));
    BigInt *h_curr  = (BigInt *)malloc(sizeof(BigInt));

    if (!h_prev2 || !h_prev1 || !h_curr) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Seed h(0) = 1 (artificial) and h(1) = a(1) = 2. */
    bigint_set(h_prev2, 1ULL);
    bigint_set(h_prev1, (unsigned long long)e_denominator(1));

    if (n == 1) {
        long long ans = bigint_digit_sum(h_prev1);
        free(h_prev2); free(h_prev1); free(h_curr);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(ans)); return _answer; }
    }

    for (int k = 2; k <= n; k++) {
        unsigned long long ak = (unsigned long long)e_denominator(k);
        bigint_mul_add(h_curr, h_prev1, ak, h_prev2);
        /* Rotate the three buffers instead of copying: stale h_prev2 becomes next destination. */
        BigInt *tmp = h_prev2;
        h_prev2 = h_prev1;
        h_prev1 = h_curr;
        h_curr = tmp;
    }

    long long ans = bigint_digit_sum(h_prev1);
    free(h_prev2); free(h_prev1); free(h_curr);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(ans)); return _answer; }
}