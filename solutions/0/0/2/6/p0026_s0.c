/* Solution to Euler Problem 26: Reciprocal Cycles. */
#include "runner.h"

/* Euclidean gcd; used to skip any d sharing a factor (2 or 5) with the base 10. */
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Multiplicative order of a modulo modulus (smallest k with a**k == 1 mod modulus); -1 if none.
   r is widened to long long so the r * a product cannot overflow for modulus up to a few thousand. */
static int multiplicative_order(int a, int modulus) {
    long long r = 1;
    for (int k = 1; k < modulus; k++) {
        r = r * a % modulus;
        if (r == 1)
            return k;
    }
    return -1; /* no order found */
}

/* The recurring-cycle length of 1/d equals the multiplicative order of 10 modulo d
   (for d coprime to 10); return the d below the limit that maximises it. Since that order
   is < d, only the top window of denominators can win, so just those are scanned. O(limit^2). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int limit = parse_int(argv[1]);

    int best_len = -1;
    int best_d = -1;

    /* Mirror Python: range(max(limit // 10, 10)) iterations */
    int iters = limit / 10;
    if (iters < 10) iters = 10;

    for (int i = 0; i < iters; i++) {
        int d = limit - i;
        if (d <= 6) continue;
        if (gcd(d, 10) != 1) continue;
        int order = multiplicative_order(10, d);
        if (order < 0) continue;
        if (order > best_len || (order == best_len && d > best_d)) {
            best_len = order;
            best_d = d;
        }
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)best_d)); return _answer; }
}
