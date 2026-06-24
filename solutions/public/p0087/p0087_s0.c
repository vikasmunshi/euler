/* Solution to Euler Problem 87: Prime Power Triples. */
#include "runner.h"
#include <math.h>

/* Sieve of Sundaram: returns array of primes up to max_num, sets *count.
   Unmarked position k corresponds to the odd prime 2k+1. */
static int *primes_sundaram_sieve(int max_num, int *count) {
    *count = 0;
    if (max_num < 2) return NULL;

    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;

    for (int i = 1; i <= n; i++) {
        for (int j = i; i + j + 2 * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }

    /* Count primes */
    int cap = 1; /* include 2 */
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) cap++;
    }

    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(marked); return NULL; }

    int idx = 0;
    primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }

    free(marked);
    *count = idx;
    return primes;
}

/* Enumerate p^2 + q^3 + r^4 over primes up to sqrt(N), counting distinct sums below N.
   Ascending prime lists let each nested loop break once its partial sum exceeds the budget,
   so the nominally cubic search visits only the few million productive triples; one sieve to
   sqrt(N) covers all three exponent roles since the square term imposes the weakest base bound.
   A direct-addressed byte array gives collision-free O(1) deduplication over the fixed value range. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long max_num = (argc >= 2) ? parse_int(argv[1]) : 50000000LL;

    int sqrt_max = (int)sqrt((double)max_num);
    int prime_count = 0;
    int *primes = primes_sundaram_sieve(sqrt_max, &prime_count);
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    /* Use a bitset for deduplication */
    unsigned char *seen = calloc((size_t)max_num, 1);
    if (!seen) { free(primes); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    long long max_quadruple_cube = max_num - 4;   /* smallest square is 2^2=4 */
    long long max_quadruple      = max_quadruple_cube - 8; /* smallest cube is 2^3=8 */

    long long count = 0;

    for (int i4 = 0; i4 < prime_count; i4++) {
        /* cast to long long before multiplying so the fourth power cannot overflow int */
        long long quadruple = (long long)primes[i4] * primes[i4] * primes[i4] * primes[i4];
        if (quadruple > max_quadruple) break;

        for (int i3 = 0; i3 < prime_count; i3++) {
            long long cube = (long long)primes[i3] * primes[i3] * primes[i3];
            long long quadruple_cube = quadruple + cube;
            if (quadruple_cube > max_quadruple_cube) break;

            for (int i2 = 0; i2 < prime_count; i2++) {
                long long square = (long long)primes[i2] * primes[i2];
                long long number = quadruple_cube + square;
                if (number >= max_num) break;

                if (!seen[number]) {
                    seen[number] = 1;
                    count++;
                }
            }
        }
    }

    free(seen);
    free(primes);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}