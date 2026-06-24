/* Solution to Euler Problem 63: Powerful Digit Counts. */
#include "runner.h"
#include <math.h>

/* Count the decimal digits of a long long. */
static int ll_digit_count(long long x) {
    if (x <= 0) return 0;
    int count = 0;
    while (x > 0) {
        count++;
        x /= 10;
    }
    return count;
}

/* Compute base^exp with integer arithmetic, returning -1 if it would overflow long long. */
static long long ipow(long long base, int exp) {
    long long result = 1;
    for (int e = 0; e < exp; e++) {
        /* Guard before multiplying: signed overflow is undefined, so it must be caught up front. */
        if (result > 0 && base > 0 && result > (long long)9e18 / base)
            return -1; /* overflow */
        result *= base;
    }
    return result;
}

/* Count n-digit n-th powers by scanning n upward until no base qualifies; O(1) bounded search.
 * Only bases 1..9 can work (base >= 10 gives n+1 digits), and digit count grows sublinearly in n,
 * so n is bounded near 21. A cheap log10 digit screen precedes the exact integer confirmation. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc;
    (void)argv;

    long long result = 0;
    int n = 1;

    while (1) {
        int solutions_this_n = 0;

        /* All valid bases must be 1..9 (base >= 10 gives b^n >= 10^n, too many digits) */
        for (int b = 1; b <= 9; b++) {
            /* Primary screen via log10: a positive x has floor(log10(x)) + 1 digits */
            double log_digits;
            if (b == 1) {
                /* 1^n = 1 always has 1 digit */
                log_digits = 0.0;
            } else {
                log_digits = (double)n * log10((double)b);
            }
            int digits_approx = (int)floor(log_digits) + 1;

            if (digits_approx == n) {
                /* Confirm with exact integer arithmetic when it does not overflow */
                long long r = ipow((long long)b, n);
                if (r > 0) {
                    /* Exact check */
                    if (ll_digit_count(r) == n) {
                        solutions_this_n++;
                    }
                } else {
                    /* Overflow means the number has more than 18 digits,
                     * which would be far more than n for bases 1-9 in practice.
                     * Trust the log10 estimate. */
                    solutions_this_n++;
                }
            }
        }

        if (solutions_this_n == 0) break;

        result += solutions_this_n;
        n++;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}