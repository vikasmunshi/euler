/* Solution to Euler Problem 72: Counting Fractions. */
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_d = parse_int(argv[1]);

    /* Sum Euler's totient phi(d) for d in 2..max_d via a multiplicative sieve; O(N log log N).
       phi(d) counts reduced proper fractions with denominator exactly d. A cell still equal to its
       index marks a prime, which applies (p-1)/p to every multiple; each totient is finalised
       before its index is read. result fits in long long (about 3.0e11 at max_d = 1000000). */
    long long *euler_totients = malloc((size_t)(max_d + 1) * sizeof(long long));
    if (!euler_totients) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    for (int i = 0; i <= max_d; i++) {
        euler_totients[i] = i;
    }

    long long result = 0;
    for (int n = 2; n <= max_d; n++) {
        if (euler_totients[n] == n) {
            /* n is prime */
            for (int j = n; j <= max_d; j += n) {
                /* Divide before multiply: euler_totients[j] is divisible by the fresh prime n. */
                euler_totients[j] = euler_totients[j] / n * (n - 1);
            }
        }
        result += euler_totients[n];
    }

    free(euler_totients);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}