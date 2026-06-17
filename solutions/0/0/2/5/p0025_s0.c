/* Solution to Euler Problem 25: $1000$-digit Fibonacci Number. */
#include "runner.h"

/*
 * Big-integer addition using arrays of decimal digits (base 10^9 limbs).
 * Each limb stores up to 9 decimal digits.
 */

#define BASE      1000000000ULL
#define MAX_LIMBS 200  /* 200 * 9 = 1800 digits, more than enough */

typedef struct {
    unsigned long long limbs[MAX_LIMBS];
    int len;
} BigInt;

static void bigint_set_one(BigInt *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->limbs[0] = 1;
    a->len = 1;
}

/* dst = a + b */
static void bigint_add(BigInt *dst, const BigInt *a, const BigInt *b) {
    int maxlen = a->len > b->len ? a->len : b->len;
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < maxlen || carry; i++) {
        unsigned long long sum = carry;
        if (i < a->len) sum += a->limbs[i];
        if (i < b->len) sum += b->limbs[i];
        dst->limbs[i] = sum % BASE;
        carry = sum / BASE;
    }
    dst->len = i;
}

/* Return total decimal digit count of a */
static int bigint_digit_count(const BigInt *a) {
    if (a->len == 0) return 1;
    /* count digits in the top limb */
    unsigned long long top = a->limbs[a->len - 1];
    int d = 0;
    while (top > 0) { top /= 10; d++; }
    if (d == 0) d = 1;
    return d + (a->len - 1) * 9;
}

/*
 * Iterate the Fibonacci recurrence with base-10^9 big-integer addition until a
 * term first reaches n decimal digits; return that term's index. O(n^2) limb
 * operations: ~n terms, each addition touching up to O(n/9) limbs. Mirrors the
 * Python sibling, hand-rolling the big integer C lacks natively.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int n = (argc >= 2) ? parse_int(argv[1]) : 1000;

    BigInt a, b, tmp;
    bigint_set_one(&a);
    bigint_set_one(&b);

    long long i = 2;
    while (bigint_digit_count(&b) < n) {
        /* tmp = a + b */
        bigint_add(&tmp, &a, &b);
        /* a = b */
        memcpy(&a, &b, sizeof(BigInt));
        /* b = tmp */
        memcpy(&b, &tmp, sizeof(BigInt));
        i++;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(i)); return _answer; }
}
