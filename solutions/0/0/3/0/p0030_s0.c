/* Solution to Euler Problem 30: Digit Fifth Powers. */
#include "runner.h"
#include <math.h>

/* Integer power base^exp via repeated multiplication (no floating-point rounding risk). */
static long long ipow(long long base, int exp) {
    long long result = 1;
    for (int i = 0; i < exp; i++) result *= base;
    return result;
}

/* Sum of the nth powers of the decimal digits of num. */
static long long digit_power_sum(long long num, int n) {
    long long s = 0;
    while (num > 0) {
        int d = (int)(num % 10);
        s += ipow(d, n);
        num /= 10;
    }
    return s;
}

/* Enumerate sorted digit multisets (the digit-power sum is order-independent), capped at
 * ceil(log10(n*9^n)) digits since no longer number can reach its own digit-power sum, and keep
 * those whose sum reproduces itself; O(C(10+k-1, k) * k) for k digits. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int n = parse_int(argv[1]);

    /* upper_bound_num_digits = ceil(log(n * 9^n, 10)) */
    double max_sum = (double)n * pow(9.0, (double)n);
    int upper_bound_num_digits = (int)ceil(log10(max_sum));

    int k = upper_bound_num_digits;

    /* State array encoding the current multiset: indices[0..k-1] each in [0..9], non-decreasing,
     * standing in for combinations_with_replacement(range(10), k) */
    int *indices = calloc((size_t)k, sizeof(int));
    if (!indices) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long total = 0;

    /* Iterate over all non-decreasing sequences of length k from {0,...,9} */
    while (1) {
        /* Compute sum of nth powers of current multiset */
        long long num = 0;
        for (int i = 0; i < k; i++) {
            num += ipow(indices[i], n);
        }

        /* Keep num only if it is a genuine narcissistic number: > 9 and equal
         * to the digit-power sum of its own digits */
        if (num > 9 && digit_power_sum(num, n) == num) {
            total += num;
        }

        /* Advance the multiset lexicographically: find the rightmost slot not
         * yet 9, increment it, and flood-fill positions to its right with that
         * value to keep the non-decreasing canonical form (each multiset once) */
        int pos = k - 1;
        while (pos >= 0 && indices[pos] == 9) {
            pos--;
        }
        if (pos < 0) break;
        int val = indices[pos] + 1;
        for (int i = pos; i < k; i++) {
            indices[i] = val;
        }
    }

    free(indices);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}