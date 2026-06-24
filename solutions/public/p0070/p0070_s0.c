/* Solution to Euler Problem 70: Totient Permutation. */
#include "runner.h"
#include <math.h>

/* Sieve of Eratosthenes returning primes up to max_val in a flat array; O(N log log N). */
static int *sieve_primes(int max_val, int *count) {
    char *is_composite = calloc((size_t)(max_val + 1), 1);
    if (!is_composite) { *count = 0; return NULL; }
    /* Capacity estimated from the prime-counting approximation; realloc defensively if exceeded. */
    int cap = (int)(max_val / (log((double)max_val) - 1.1)) + 1000;
    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(is_composite); *count = 0; return NULL; }
    int n = 0;
    for (int i = 2; i <= max_val; i++) {
        if (!is_composite[i]) {
            primes[n++] = i;
            if (n >= cap) {
                cap *= 2;
                int *tmp = realloc(primes, (size_t)cap * sizeof(int));
                if (!tmp) { free(primes); free(is_composite); *count = 0; return NULL; }
                primes = tmp;
            }
            if ((long long)i * i <= max_val) {
                for (long long j = (long long)i * i; j <= max_val; j += i)
                    is_composite[j] = 1;
            }
        }
    }
    free(is_composite);
    *count = n;
    return primes;
}

/* Test whether a and b are digit permutations via an allocation-free 10-bucket frequency count. */
static int is_digit_permutation(long long a, long long b) {
    int count[10] = {0};
    while (a > 0) { count[a % 10]++; a /= 10; }
    while (b > 0) { count[b % 10]--; b /= 10; }
    for (int i = 0; i < 10; i++)
        if (count[i] != 0) return 0;
    return 1;
}

/* Search semiprimes n = p1*p2 with both primes near sqrt(limit), since n/phi(n) = prod p/(p-1)
   is minimised by few large factors; phi(p1*p2) = (p1-1)*(p2-1) needs no factorisation. Bounding
   p1 to [sqrt(limit)/2, sqrt(limit)] and p2 to (p1+2, limit/p1] keeps the search to a narrow band. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int limit = (argc > 1) ? parse_int(argv[1]) : 10000000;
    int sqrt_n = (int)sqrt((double)limit);
    int min_prime_1 = sqrt_n / 2;
    int max_prime_1 = sqrt_n;
    int max_prime_2 = limit; /* upper bound for sieve */

    int pcount = 0;
    int *primes = sieve_primes(max_prime_2, &pcount);
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    double min_ratio = 1e18;
    long long min_n = 0;

    /* Advance to the first prime greater than min_prime_1. */
    int idx1_start = 0;
    while (idx1_start < pcount && primes[idx1_start] <= min_prime_1)
        idx1_start++;

    for (int i = idx1_start; i < pcount; i++) {
        long long p1 = primes[i];
        if (p1 > max_prime_1) break;

        long long max_p2 = limit / p1;
        long long min_p2 = p1 + 2;

        /* Advance p2 past p1+2 so the two primes are distinct and not twins. */
        int idx2_start = i + 1;
        while (idx2_start < pcount && primes[idx2_start] <= (int)(p1 + 2))
            idx2_start++;

        for (int j = idx2_start; j < pcount; j++) {
            long long p2 = primes[j];
            if (p2 > max_p2) break;

            long long number = p1 * p2;
            long long totient = (p1 - 1) * (p2 - 1);

            if (is_digit_permutation(number, totient)) {
                double ratio = (double)number / (double)totient;
                if (ratio < min_ratio) {
                    min_ratio = ratio;
                    min_n = number;
                }
            }
        }
    }

    free(primes);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(min_n)); return _answer; }
}