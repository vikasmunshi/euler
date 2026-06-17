/* Solution to Euler Problem 55: Lychrel Numbers. */
#include "runner.h"

/* Big number represented as array of digits (base 10), little-endian */
#define MAX_DIGITS 128

typedef struct {
    int digits[MAX_DIGITS];
    int len;
} BigNum;

/* Load a non-negative long long into a little-endian base-10 BigNum. */
static void bignum_from_ll(BigNum *b, long long n) {
    b->len = 0;
    if (n == 0) {
        b->digits[0] = 0;
        b->len = 1;
        return;
    }
    while (n > 0) {
        b->digits[b->len++] = (int)(n % 10);
        n /= 10;
    }
}

/* result = a + reverse(a); little-endian index i is big-endian index n-1-i, so no reversed copy is built. */
static void bignum_add_reverse(BigNum *result, const BigNum *a) {
    int carry = 0;
    int n = a->len;
    result->len = n;
    for (int i = 0; i < n; i++) {
        int sum = a->digits[i] + a->digits[n - 1 - i] + carry;
        result->digits[i] = sum % 10;
        carry = sum / 10;
    }
    if (carry) {
        result->digits[result->len++] = carry;
    }
}

/* Return 1 if the decimal digits read the same in both directions. */
static int bignum_is_palindrome(const BigNum *b) {
    int n = b->len;
    for (int i = 0; i < n / 2; i++) {
        if (b->digits[i] != b->digits[n - 1 - i])
            return 0;
    }
    return 1;
}

/* True if number yields no palindrome within max_iterations reverse-and-add steps (test the result, not seed). */
static int is_lychrel(long long number, int max_iterations) {
    BigNum a, result;
    bignum_from_ll(&a, number);

    for (int iter = 0; iter < max_iterations; iter++) {
        bignum_add_reverse(&result, &a);
        if (bignum_is_palindrome(&result))
            return 0;
        a = result;
    }
    return 1;
}

/* Count Lychrel numbers up to max_limit via bounded big-integer reverse-and-add; O(max_limit * max_iterations). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_iterations = parse_int(argv[1]);
    int max_limit = parse_int(argv[2]);

    long long count = 0;
    for (int i = 1; i <= max_limit; i++) {
        if (is_lychrel((long long)i, max_iterations))
            count++;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}