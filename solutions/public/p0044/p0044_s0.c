/* Solution to Euler Problem 44: Pentagon Numbers. */
#include "runner.h"
#include <math.h>

/* Return the n-th pentagonal number via the closed form n(3n-1)/2. */
static long long nth_pentagonal(long long n) {
    return n * (3 * n - 1) / 2;
}

/* Test pentagonality by inverting the quadratic, then round-and-verify in exact integer
   arithmetic to avoid floating-point boundary errors. */
static int is_pentagonal(long long m) {
    double disc = 1.0 + 24.0 * (double)m;
    double sq = sqrt(disc);
    double n = (1.0 + sq) / 6.0;
    long long ni = (long long)round(n);
    return (ni > 0) && (nth_pentagonal(ni) == m);
}

/* Scan outer index i upward and inner index j downward, returning the first pair whose sum and
   difference are both pentagonal; the descending inner loop makes that first hit the minimal
   difference for each i, and the ascending outer loop makes it the global minimum.
   O(i_answer^2) constant-time pentagonality tests. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;
    for (long long i = 1; ; i++) {
        long long p_i = nth_pentagonal(i);
        for (long long j = i - 1; j >= 1; j--) {
            long long p_j = nth_pentagonal(j);
            long long diff = p_i - p_j;
            long long sum  = p_i + p_j;
            if (is_pentagonal(diff) && is_pentagonal(sum)) {
                { snprintf(_answer, sizeof _answer, "%lld", (long long)(diff)); return _answer; }
            }
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}