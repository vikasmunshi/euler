/* Solution to Euler Problem 50: Consecutive Prime Sum. */
#include "runner.h"

/* Return all primes up to max_num via the Sieve of Sundaram; O(n log log n). */
static int *primes_sundaram_sieve(int max_num, int *out_count) {
    *out_count = 0;
    if (max_num < 2) {
        int *p = malloc(sizeof(int));
        return p; /* return empty but non-null */
    }

    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;

    for (int i = 1; i <= n; i++) {
        /* cast to long long so i + j + 2*i*j cannot overflow 32-bit during the bound test */
        for (int j = i; (long long)i + j + 2LL * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }

    int count = 1; /* for prime 2 */
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) count++;
    }

    int *primes = malloc((size_t)count * sizeof(int));
    if (!primes) { free(marked); return NULL; }

    int idx = 0;
    primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }

    free(marked);
    *out_count = count;
    return primes;
}

/* Prefix sums make each consecutive-prime sum one subtraction; two monotonicity prunes
   (break on exceeding the limit, skip runs no longer than the current best) keep the
   nominally quadratic search near-linear. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_limit = (argc > 1) ? parse_int(argv[1]) : 1000000;
    if (max_limit < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }

    int prime_count = 0;
    int *primes = primes_sundaram_sieve(max_limit, &prime_count);
    if (!primes || prime_count == 0) {
        free(primes);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }
    }

    /* prefix sums array of size prime_count+1; long long because the sum of primes below one
       million is roughly 37 billion, far past the 32-bit signed limit */
    long long *prime_sums = malloc((size_t)(prime_count + 1) * sizeof(long long));
    if (!prime_sums) { free(primes); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    prime_sums[0] = 0;
    for (int i = 0; i < prime_count; i++) {
        prime_sums[i + 1] = prime_sums[i] + primes[i];
    }

    /* boolean sieve for O(1) primality checks, size max_limit+1 (flat byte array for cache locality) */
    unsigned char *is_prime = calloc((size_t)(max_limit + 1), 1);
    if (!is_prime) { free(prime_sums); free(primes); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }
    for (int i = 0; i < prime_count; i++) {
        if (primes[i] <= max_limit)
            is_prime[primes[i]] = 1;
    }

    int best_length = 0;
    long long best_prime = 0;

    /* len of prime_sums is prime_count+1, indices 0..prime_count */
    int ps_len = prime_count + 1;

    for (int i = 0; i < ps_len; i++) {
        /* start past the current best: any larger j gives a run no longer than best */
        int j_start = i - best_length - 1;
        if (j_start < 0) continue; /* can't beat current best */
        for (int j = j_start; j >= 0; j--) {
            long long possible_prime = prime_sums[i] - prime_sums[j];
            /* prefix sums increase as j shrinks, so once past the limit every smaller j is too */
            if (possible_prime > (long long)max_limit) break;
            if (possible_prime >= 2) {
                int pp = (int)possible_prime;
                if (is_prime[pp]) {
                    best_length = i - j;
                    best_prime = possible_prime;
                }
            }
        }
    }

    free(is_prime);
    free(prime_sums);
    free(primes);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(best_prime)); return _answer; }
}