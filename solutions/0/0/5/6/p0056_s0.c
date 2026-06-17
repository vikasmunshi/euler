/* Solution to Euler Problem 56: Powerful Digit Sum. */
#include "runner.h"

/* Big integer as a little-endian array of single base-10 digits (index 0 = units place),
 * chosen so the digit sum is a trivial loop with no extraction. */
typedef struct {
    int *digits;
    int len;
    int cap;
} BigInt;

/* Allocate a zeroed BigInt with the given digit capacity. */
static BigInt *bigint_new(int cap) {
    BigInt *b = malloc(sizeof(BigInt));
    b->cap = cap;
    b->len = 1;
    b->digits = calloc((size_t)cap, sizeof(int));
    b->digits[0] = 0;
    return b;
}

/* Release the digit buffer and the struct. */
static void bigint_free(BigInt *b) {
    free(b->digits);
    free(b);
}

/* Set big integer to a small value */
static void bigint_set(BigInt *b, int val) {
    memset(b->digits, 0, (size_t)b->cap * sizeof(int));
    b->len = 0;
    while (val > 0) {
        b->digits[b->len++] = val % 10;
        val /= 10;
    }
    if (b->len == 0) {
        b->len = 1;
        b->digits[0] = 0;
    }
}

/* Multiply big integer by a small integer in place via left-to-right carry propagation. */
static void bigint_mul_int(BigInt *b, int m) {
    long long carry = 0;
    for (int i = 0; i < b->len; i++) {
        /* widen to long long before multiplying to avoid overflow in digit*m + carry */
        long long prod = (long long)b->digits[i] * m + carry;
        b->digits[i] = (int)(prod % 10);
        carry = prod / 10;
    }
    while (carry > 0) {
        if (b->len >= b->cap) {
            /* doubling-realloc fallback in case the pre-allocated bound was underestimated */
            b->cap *= 2;
            b->digits = realloc(b->digits, (size_t)b->cap * sizeof(int));
        }
        b->digits[b->len++] = (int)(carry % 10);
        carry /= 10;
    }
}

/* Sum the digits directly, exploiting the base-10 representation. */
static long long bigint_digit_sum(BigInt *b) {
    long long s = 0;
    for (int i = 0; i < b->len; i++) {
        s += b->digits[i];
    }
    return s;
}

/* Brute-force the top 100 bases and top 10 exponents below 10^num_digits, maximizing the digit
 * sum of base^exp; powers are built incrementally (base^exp_start once, then one scalar multiply
 * per subsequent exponent). O(N^2) pairs each costing O(N log N) bignum digit work. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int num_digits = parse_int(argv[1]);

    /* stop_at = 10^num_digits */
    int stop_at = 1;
    for (int i = 0; i < num_digits; i++) stop_at *= 10;

    int base_start = stop_at - 100;
    if (base_start < 1) base_start = 1;
    int exp_start = stop_at - 10;
    if (exp_start < 1) exp_start = 1;

    /* Estimate max digits needed: base=99, exp=999...
     * digits ~ exp * log10(base) + 2
     * For num_digits=3: ~999 * 2 + 10 = ~2008 */
    int max_exp = stop_at - 1;
    int max_base = stop_at - 1;
    /* max digits ~ max_exp * ceil(log10(max_base)) + 10 */
    /* Use a safe upper bound */
    int max_digits = max_exp * (num_digits + 1) + 100;
    if (max_digits < 300) max_digits = 300;

    BigInt *b = bigint_new(max_digits);
    long long best = 0;

    for (int base = base_start; base < stop_at; base++) {
        /* Compute base^exp for exp in [exp_start, stop_at) */
        /* First compute base^exp_start */
        bigint_set(b, 1);
        for (int e = 0; e < exp_start; e++) {
            bigint_mul_int(b, base);
        }
        long long ds = bigint_digit_sum(b);
        if (ds > best) best = ds;

        for (int exp = exp_start + 1; exp < stop_at; exp++) {
            bigint_mul_int(b, base);
            ds = bigint_digit_sum(b);
            if (ds > best) best = ds;
        }
    }

    bigint_free(b);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(best)); return _answer; }
}