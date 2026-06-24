/* Solution to Euler Problem 71: Ordered Fractions. */
#include "runner.h"

/* Euclidean GCD, iterative form, for reducing the candidate fraction. */
static long long gcd(long long a, long long b) {
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

const char *solve(int argc, char *argv[]) {
    /* Farey neighbour of 3/7 in F_N: the immediate left fraction is (3k - 1)/(7k) with
       k = floor(N/7), since 3/7 - (3k-1)/(7k) = 1/(7k) is the smallest achievable gap. O(1). */
    static char _answer[32];
    long long max_d = parse_int(argv[1]);
    long long k = max_d / 7;
    /* result = 3/7 - 1/(7*k) = (3k - 1) / (7k) */
    long long num = 3 * k - 1;
    long long den = 7 * k;
    long long g = gcd(num, den);
    num /= g;
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(num)); return _answer; }
}