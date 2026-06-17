/* Solution to Euler Problem 57: Square Root Convergents. */
#include "runner.h"
#include <stdint.h>

/* Big integer: base 10^9, little-endian limbs. Base 10^9 makes the decimal
   digit count nearly free - each non-top limb contributes exactly nine digits. */
#define BASE 1000000000ULL
#define MAX_LIMBS 512

typedef struct {
    uint32_t limbs[MAX_LIMBS];
    int size;
} BigInt;

/* Initialise a BigInt from a 64-bit value, splitting it into base-10^9 limbs. */
static void bi_set_int(BigInt *a, uint64_t val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->size = 0;
    if (val == 0) {
        a->limbs[0] = 0;
        a->size = 1;
        return;
    }
    int i = 0;
    while (val > 0 && i < MAX_LIMBS) {
        a->limbs[i++] = (uint32_t)(val % BASE);
        val /= BASE;
    }
    a->size = i;
}

/* a = b + 2*c (next convergent numerator), propagating carries across limbs. */
static void bi_add_twice(BigInt *a, const BigInt *b, const BigInt *c) {
    int n = b->size > c->size ? b->size : c->size;
    uint64_t carry = 0;
    int i;
    for (i = 0; i < n || carry; i++) {
        if (i >= MAX_LIMBS) break;
        uint64_t sum = carry;
        if (i < b->size) sum += b->limbs[i];
        if (i < c->size) sum += 2ULL * c->limbs[i];
        a->limbs[i] = (uint32_t)(sum % BASE);
        carry = sum / BASE;
    }
    a->size = i;
    while (a->size > 1 && a->limbs[a->size - 1] == 0) a->size--;
}

/* a = b + c (next convergent denominator), propagating carries across limbs. */
static void bi_add(BigInt *a, const BigInt *b, const BigInt *c) {
    int n = b->size > c->size ? b->size : c->size;
    uint64_t carry = 0;
    int i;
    for (i = 0; i < n || carry; i++) {
        if (i >= MAX_LIMBS) break;
        uint64_t sum = carry;
        if (i < b->size) sum += b->limbs[i];
        if (i < c->size) sum += c->limbs[i];
        a->limbs[i] = (uint32_t)(sum % BASE);
        carry = sum / BASE;
    }
    a->size = i;
    while (a->size > 1 && a->limbs[a->size - 1] == 0) a->size--;
}

/* Count decimal digits: 9 per non-top limb, plus the digits of the top limb. */
static int bi_decimal_digits(const BigInt *a) {
    if (a->size == 0) return 1;
    int top = a->size - 1;
    uint32_t top_limb = a->limbs[top];
    int d = top * 9;
    if (top_limb == 0) {
        d += 1;
    } else {
        uint32_t t = top_limb;
        int cnt = 0;
        while (t > 0) { cnt++; t /= 10; }
        d += cnt;
    }
    return d;
}

/* Iterate the sqrt(2) convergent recurrence (p, q) -> (p + 2q, p + q) with a
   base-10^9 big integer, counting steps where the numerator has more decimal
   digits than the denominator; O(n^2) from adding linearly growing values. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int expansions = (argc >= 2) ? parse_int(argv[1]) : 1000;

    BigInt num, den, new_num, new_den;
    bi_set_int(&num, 1);
    bi_set_int(&den, 1);

    long long result = 0;

    for (int i = 0; i < expansions; i++) {
        /* Compute both new values before overwriting either: the new numerator
           depends on the old denominator and vice versa. */
        bi_add_twice(&new_num, &num, &den);
        bi_add(&new_den, &num, &den);

        num = new_num;
        den = new_den;

        int dnum = bi_decimal_digits(&num);
        int dden = bi_decimal_digits(&den);
        if (dnum > dden) result++;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}